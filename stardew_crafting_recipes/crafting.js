const searchInput = document.querySelector("#searchBox");
const statusLine = document.querySelector("#status");
const resultsBox = document.querySelector("#results");
const sourceFilter = document.querySelector("#sourceFilter");
const unlockFilter = document.querySelector("#unlockFilter");

let recipes = [];
let baseStatus = "";

const get = (obj, key) => (obj?.[key] ?? "").toString().trim();

const escapeHtml = (value) => {
    const str = value === undefined || value === null ? "" : String(value);
    return str
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
};

const formatMultiline = (value) =>
    escapeHtml(value)
        .split("\n")
        .join("<br>");

const normalize = (str) =>
    str
        ? str
            .toString()
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase()
        : "";

const buildRecipeEntity = (raw) => {
    const name = get(raw, "名称");
    const nameEN = get(raw, "名称_EN");
    const description = get(raw, "描述");
    const materials = raw["材料"] || [];
    const output = raw["产物"] || {};
    const category = get(raw, "分类");
    const unlock = get(raw, "解锁条件");
    const unlockDescription = get(raw, "解锁条件描述");
    const source = get(raw, "来源");
    const imageUrl = get(raw, "图片链接");

    const keywords = normalize(
        [name, nameEN, ...materials.map(m => m.名称), output.名称, category, unlock, source].filter(Boolean).join(" | ")
    );

    return {
        name,
        nameEN,
        description,
        materials,
        output,
        category,
        unlock,
        unlockDescription,
        source,
        imageUrl,
        keywords,
    };
};

/**
 * 将解锁条件归类为更简洁的类别
 */
function categorizeUnlock(unlock) {
    if (!unlock) return "";

    // 技能类（耕种、钓鱼、采集、采矿、战斗、法术之道等）
    if (unlock.includes("技能") || (unlock.includes("Lv.") && !unlock.includes("购买"))) {
        const skillMatch = unlock.match(/^(.+?)(技能|Lv\.)/);
        if (skillMatch) {
            return skillMatch[1].trim() + "技能";
        }
    }

    // 购买类（各种商店购买）
    if (unlock.includes("购买") || unlock.includes("商店")) {
        return "商店购买";
    }

    // 特殊订单
    if (unlock.includes("特殊订单")) {
        return "特殊订单";
    }

    // NPC事件/好感（心数事件、好感度、剧情）
    if ((unlock.includes("心") && (unlock.includes("事件") || unlock.includes("好感") || unlock.includes("剧情"))) ||
        unlock.includes("好感度")) {
        return "NPC事件/好感";
    }

    // 其他常见类别
    if (unlock.includes("默认")) return "默认解锁";
    if (unlock.includes("赠予") || unlock.includes("传授")) return "NPC赠予";
    if (unlock.includes("完成") || unlock.includes("获得") || (unlock.includes("解锁") && !unlock.includes("默认"))) return "任务/活动获得";
    if (unlock.includes("触发") || unlock.includes("升级")) return "事件触发";
    if (unlock.includes("集齐") || unlock.includes("捐赠")) return "收集类";

    // 其他保持原样
    return unlock;
}

function collectUniqueValues(values) {
    const seen = new Set();
    const list = [];
    values.forEach((value) => {
        if (!value) return;
        if (!seen.has(value)) {
            seen.add(value);
            list.push(value);
        }
    });
    const collator = new Intl.Collator("zh-Hans-CN");
    list.sort((a, b) => collator.compare(a, b));
    return list;
}

function setSelectOptions(select, values, defaultLabel) {
    if (!select) return;

    const options = [`<option value="">${escapeHtml(defaultLabel)}</option>`];
    values.forEach((value) => {
        options.push(
            `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
        );
    });
    select.innerHTML = options.join("");
}

function populateFilterOptions() {
    const sourceValues = collectUniqueValues(recipes.map((recipe) => recipe.source));
    // 对解锁条件进行归类
    const unlockCategories = collectUniqueValues(
        recipes.map((recipe) => categorizeUnlock(recipe.unlock))
    );

    setSelectOptions(sourceFilter, sourceValues, "全部来源");
    setSelectOptions(unlockFilter, unlockCategories, "全部解锁");
}

function getFilterValue(select) {
    return (select && select.value) || "";
}

function matchesFilters(recipe, sourceValue, unlockValue) {
    if (sourceValue && recipe.source !== sourceValue) {
        return false;
    }

    // 使用归类后的解锁条件进行匹配
    if (unlockValue && categorizeUnlock(recipe.unlock) !== unlockValue) {
        return false;
    }

    return true;
}

function updateResults() {
    const rawTerm = (searchInput?.value || "").trim();
    const term = normalize(rawTerm);
    const tokens = term ? term.split(" ").filter(Boolean) : [];

    const sourceValue = getFilterValue(sourceFilter);
    const unlockValue = getFilterValue(unlockFilter);
    const hasFilters = Boolean(sourceValue || unlockValue);

    let filtered = recipes;
    if (tokens.length) {
        filtered = filtered.filter((recipe) =>
            tokens.every((token) => recipe.keywords.includes(token))
        );
    }

    filtered = filtered.filter((recipe) =>
        matchesFilters(recipe, sourceValue, unlockValue)
    );

    renderResults(filtered, rawTerm, hasFilters);
}

function updateStatus(text) {
    if (statusLine) {
        statusLine.textContent = text;
    }
}

function setBaseStatus(text) {
    baseStatus = text;
    updateStatus(text);
}

function renderEmptyHint(message) {
    resultsBox.innerHTML = `<div class="empty-hint">${escapeHtml(message)}</div>`;
}

function renderMaterialsList(materials) {
    if (!materials || materials.length === 0) return "";

    const rows = materials
        .map((item) => {
            return `
        <div class="item-row">
          <span class="item-name">${escapeHtml(item.名称 || item.id)}</span>
          <span class="item-quantity">× ${item.数量}</span>
        </div>
      `;
        })
        .join("");

    return `
    <div class="info-item">
      <div class="info-label">所需材料</div>
      <div class="info-value item-list">${rows}</div>
    </div>
  `;
}

function renderOutput(output) {
    if (!output || !output.id) return "";

    return `
    <div class="info-item">
      <div class="info-label">产出</div>
      <div class="info-value item-list">
        <div class="item-row">
          <span class="item-name">${escapeHtml(output.名称 || output.id)}</span>
          <span class="item-quantity">× ${output.数量}</span>
        </div>
      </div>
    </div>
  `;
}

function renderField(label, value, tooltip = "") {
    if (!value) return "";

    const titleAttr = tooltip ? ` title="${escapeHtml(tooltip)}" data-tooltip="${escapeHtml(tooltip)}"` : "";
    const tooltipClass = tooltip ? " has-tooltip" : "";

    return `
    <div class="info-item">
      <div class="info-label">${escapeHtml(label)}</div>
      <div class="info-value${tooltipClass}"${titleAttr}>${escapeHtml(value)}</div>
    </div>
  `;
}

function createCard(recipe) {
    const card = document.createElement("article");
    const isCraftable = Boolean(recipe.output?.["是大型可制作物"]);
    card.className = `sv-card recipe-card ${isCraftable ? "card-craftable" : "card-object"}`;

    const image = recipe.imageUrl
        ? `<div class="thumb-slot ${isCraftable ? "thumb-slot-craftable" : "thumb-slot-object"}">
        <img class="thumb" src="${escapeHtml(recipe.imageUrl)}" alt="${escapeHtml(
            recipe.name
        )}" loading="lazy">
      </div>`
        : "";

    card.innerHTML = `
    ${image}
    <div class="title-line">
      <div>
        <h2>${escapeHtml(recipe.name || "未知配方")}</h2>
        ${recipe.description
            ? `<p class="desc">${formatMultiline(recipe.description)}</p>`
            : ""
        }
      </div>
    </div>
    <div class="info-grid">
      ${renderMaterialsList(recipe.materials)}
      ${renderOutput(recipe.output)}
      ${renderField("解锁条件", recipe.unlock, recipe.unlockDescription)}
      ${renderField("来源", recipe.source)}
    </div>
  `;

    if (image) {
        const thumb = card.querySelector(".thumb");
        const thumbSlot = card.querySelector(".thumb-slot");
        if (thumb && thumbSlot) {
            thumb.addEventListener("error", () => {
                thumbSlot.remove();
                card.classList.add("no-thumb");
            }, { once: true });
        }
    } else {
        card.classList.add("no-thumb");
    }

    return card;
}

function renderResults(list, term, hasFilters) {
    const hasSearch = Boolean(term);
    if (!hasSearch && !hasFilters) {
        updateStatus(baseStatus);
    } else {
        updateStatus(`找到 ${list.length} 个匹配的配方`);
    }

    if (list.length === 0) {
        renderEmptyHint("没有符合条件的配方，尝试调整搜索或筛选条件。");
        return;
    }

    const frag = document.createDocumentFragment();
    list.forEach((recipe) => frag.appendChild(createCard(recipe)));
    resultsBox.innerHTML = "";
    resultsBox.appendChild(frag);
}

function handleSearch() {
    updateResults();
}

async function loadRecipeData() {
    const response = await fetch("./data/crafting_data.json", { cache: "no-store" });
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
}

async function init() {
    if (searchInput) searchInput.disabled = true;
    if (sourceFilter) sourceFilter.disabled = true;
    if (unlockFilter) unlockFilter.disabled = true;

    try {
        const raw = await loadRecipeData();
        recipes = raw.map(buildRecipeEntity);
        setBaseStatus(`共收录 ${recipes.length} 个制作配方。支持输入空格分隔多个关键词。`);
        populateFilterOptions();

        if (searchInput) {
            searchInput.disabled = false;
            searchInput.focus();
            searchInput.addEventListener("input", handleSearch);
        }
        if (sourceFilter) {
            sourceFilter.disabled = false;
            sourceFilter.addEventListener("change", updateResults);
        }
        if (unlockFilter) {
            unlockFilter.disabled = false;
            unlockFilter.addEventListener("change", updateResults);
        }

        updateResults();
    } catch (err) {
        console.error("加载配方数据失败", err);
        updateStatus("加载配方数据失败，请确认数据文件存在。");
        renderEmptyHint("暂时无法读取配方数据。");
    }
}

// 添加全局点击事件以支持移动端 Tooltip 展开
document.addEventListener("click", (e) => {
    const target = e.target.closest(".has-tooltip");
    if (target) {
        const tooltipText = target.getAttribute("data-tooltip");
        if (tooltipText) {
            let existing = target.parentElement.querySelector(".mobile-tooltip");
            if (existing) {
                existing.remove();
            } else {
                document.querySelectorAll(".mobile-tooltip").forEach(el => el.remove());
                const tooltipDiv = document.createElement("div");
                tooltipDiv.className = "mobile-tooltip";
                tooltipDiv.textContent = tooltipText;
                target.parentElement.appendChild(tooltipDiv);
            }
        }
    } else {
        document.querySelectorAll(".mobile-tooltip").forEach(el => el.remove());
    }
});

init();
