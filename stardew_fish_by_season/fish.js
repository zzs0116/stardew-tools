const searchInput = document.querySelector("#searchBox");
const statusLine = document.querySelector("#status");
const resultsBox = document.querySelector("#results");
const weatherFilter = document.querySelector("#weatherFilter");
const seasonFilter = document.querySelector("#seasonFilter");
const sourceFilter = document.querySelector("#sourceFilter");

let fishes = [];
let baseStatus = "";

const SEASON_MAP = {
  "春季": "spring",
  "夏季": "summer",
  "秋季": "fall",
  "冬季": "winter"
};

const SEASON_ORDER = ["春季", "夏季", "秋季", "冬季", "任意季节", "未知"];

const get = (obj, key) => (obj?.[key] ?? "").toString().trim();

const QUALITY_ICON_MAP = [
  { src: "./images/quality_default.png", alt: "普通品质" },
  { src: "./images/quality_silver.png", alt: "银星品质" },
  { src: "./images/quality_gold.png", alt: "金星品质" },
  { src: "./images/quality_iridium.png", alt: "铱星品质" },
];

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

const renderField = (label, value, { asChips = false, chipTheme = "" } = {}) => {
  if (!value || (Array.isArray(value) && value.length === 0)) return "";

  const renderSingleChip = (v, index, originalArray) => {
    // Determine class based on content (v) or explicit metadata if value is an object
    let content = v;
    let extraClass = chipTheme ? `season-${chipTheme}` : ""; 

    // Handle object-based value (e.g. {text: "Loc", theme: "spring"})
    if (typeof v === 'object' && v !== null && v.text) {
        content = v.text;
        if (v.theme) extraClass = `season-${v.theme}`;
    }

    // Auto-detect season only if no explicit theme is provided and it's a season string
    if (!extraClass) {
        if (typeof content === 'string') {
            if (content.includes("春")) extraClass = "season-spring";
            if (content.includes("夏")) extraClass = "season-summer";
            if (content.includes("秋")) extraClass = "season-fall";
            if (content.includes("冬")) extraClass = "season-winter";
        }
    }
    
    return `<span class="chip ${extraClass}">${escapeHtml(content)}</span>`;
  };

  const valueMarkup = Array.isArray(value)
    ? asChips
      ? `<div class="chips">${value.map(renderSingleChip).join("")}</div>`
      : formatMultiline(value.join("\n"))
    : asChips
      ? `<div class="chips">${renderSingleChip(value)}</div>`
      : formatMultiline(value);

  return `
    <div class="info-item">
      <div class="info-label">${escapeHtml(label)}</div>
      <div class="info-value">${valueMarkup}</div>
    </div>
  `;
};

const normalize = (str) =>
  str
    ? str
        .toString()
        .replace(/\s+/g, " ")
        .trim()
        .toLowerCase()
    : "";

const buildFishEntity = (raw) => {
  const name = get(raw, "名称");
  const description = get(raw, "描述");
  const price = get(raw, "价格");
  const fisherBonus = get(raw, "渔夫职业（+25%）");
  const anglerBonus = get(raw, "垂钓者职业（+50%）");
  const location = get(raw, "位置");
  const time = get(raw, "时间");
  const season = get(raw, "季节");
  const weather = get(raw, "天气");
  const source = get(raw, "来源");
  const imageUrl = get(raw, "图片链接") || get(raw, "图片");
  const isLegendary = Boolean(raw.is_legendary);
  const locationDetails = raw["位置详情"];

  const seasonList = splitTextList(season).sort((a, b) => {
    let indexA = SEASON_ORDER.indexOf(a);
    let indexB = SEASON_ORDER.indexOf(b);
    return (indexA === -1 ? 99 : indexA) - (indexB === -1 ? 99 : indexB);
  });
  const weatherList = splitTextList(weather);
  const locationList = splitTextList(location);

  const keywords = normalize(
    [name, location, time, season, weather, source].filter(Boolean).join(" | ")
  );

  return {
    name,
    description,
    price,
    fisherBonus,
    anglerBonus,
    location,
    locationList,
    time,
    season,
    seasonList,
    weather,
    weatherList,
    source,
    imageUrl,
    keywords,
    locationDetails,
    isLegendary,
  };
};

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
  
  // Custom fixed options for Season filter
  if (select.id === "seasonFilter") {
    const fixedOptions = [
      { value: "", label: defaultLabel },
      { value: "春季", label: "春季" },
      { value: "夏季", label: "夏季" },
      { value: "秋季", label: "秋季" },
      { value: "冬季", label: "冬季" },
      { value: "任意季节", label: "任意季节" },
      { value: "未知", label: "未知" }
    ];
    select.innerHTML = fixedOptions.map(opt => 
      `<option value="${escapeHtml(opt.value)}">${escapeHtml(opt.label)}</option>`
    ).join("");
    return;
  }

  const options = [`<option value="">${escapeHtml(defaultLabel)}</option>`];
  values.forEach((value) => {
    options.push(
      `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
    );
  });
  select.innerHTML = options.join("");
}

function populateFilterOptions() {
  const weatherValues = collectUniqueValues(
    fishes.flatMap((fish) => (fish.weatherList.length ? fish.weatherList : []))
  );
  // Season filter is now hardcoded in setSelectOptions, so we don't need to calculate values for it,
  // but we pass empty array or null to trigger the default logic if we hadn't hardcoded it.
  // Passing null/empty is fine as setSelectOptions handles seasonFilter ID specifically.
  const seasonValues = []; 
  const sourceValues = collectUniqueValues(fishes.map((fish) => fish.source));

  setSelectOptions(weatherFilter, weatherValues, "全部天气");
  setSelectOptions(seasonFilter, seasonValues, "全部季节");
  setSelectOptions(sourceFilter, sourceValues, "全部来源");
}

function getFilterValue(select) {
  return (select && select.value) || "";
}

function matchesFilters(fish, weatherValue, seasonValue, sourceValue) {
  if (weatherValue) {
    if (!fish.weatherList.includes(weatherValue)) {
      return false;
    }
  }

  if (seasonValue) {
    const hasSpecificSeason = fish.seasonList.includes(seasonValue);
    const hasAnySeason = fish.seasonList.includes("任意季节");
    const hasAllSeasons = fish.seasonList.includes("春季") && 
                          fish.seasonList.includes("夏季") && 
                          fish.seasonList.includes("秋季") && 
                          fish.seasonList.includes("冬季");

    if (seasonValue === "任意季节") {
        // If filter is "Any Season", match if fish is explicitly "Any Season" OR has all 4 seasons
        if (!hasAnySeason && !hasAllSeasons) {
            return false;
        }
    } else if (seasonValue === "未知") {
         if (!fish.seasonList.includes("未知")) {
             return false;
         }
    } else {
        // If filter is specific season (Spring/Summer/etc)
        // Match if it has that season OR is Any/All
        if (!hasSpecificSeason && !hasAnySeason && !hasAllSeasons) {
            return false;
        }
    }
  }

  if (sourceValue && fish.source !== sourceValue) {
    return false;
  }

  return true;
}

function updateResults() {
  const rawTerm = (searchInput?.value || "").trim();
  const term = normalize(rawTerm);
  const tokens = term ? term.split(" ").filter(Boolean) : [];

  const weatherValue = getFilterValue(weatherFilter);
  const seasonValue = getFilterValue(seasonFilter);
  const sourceValue = getFilterValue(sourceFilter);
  const hasFilters = Boolean(weatherValue || seasonValue || sourceValue);

  let filtered = fishes;
  if (tokens.length) {
    filtered = filtered.filter((fish) =>
      tokens.every((token) => fish.keywords.includes(token))
    );
  }

  filtered = filtered.filter((fish) =>
    matchesFilters(fish, weatherValue, seasonValue, sourceValue)
  );

  renderResults(filtered, rawTerm, hasFilters, seasonValue);
}

function splitTextList(value) {
  if (!value) return [];
  return value
    .split(/(?:\s*\n\s*|、|,|，)/g) // Split by newline, ideographic comma, comma, or fullwidth comma
    .map((item) => item.trim())
    .filter(Boolean);
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

function renderPriceField(label, value) {
  if (!value) return "";
  const lines = splitTextList(value);
  if (lines.length === 0) return "";
  const rows = lines
    .map((line, index) => {
      const icon = QUALITY_ICON_MAP[index] ?? QUALITY_ICON_MAP[QUALITY_ICON_MAP.length - 1];
      return `
        <div class="price-row">
          <img src="${escapeHtml(icon.src)}" alt="${escapeHtml(icon.alt)}" loading="lazy">
          <span>${escapeHtml(line)}</span>
        </div>
      `;
    })
    .join("");
  return `
    <div class="info-item">
      <div class="info-label">${escapeHtml(label)}</div>
      <div class="info-value price-list">${rows}</div>
    </div>
  `;
}

function createCard(fish, currentSeason) {
  const card = document.createElement("article");
  card.className = `sv-card fish-card ${fish.isLegendary ? "legendary" : ""}`;
  const image = fish.imageUrl
    ? `<img class="thumb" src="${escapeHtml(fish.imageUrl)}" alt="${escapeHtml(
        fish.name
      )}" loading="lazy">`
    : "";

  let displayLocationList = fish.locationList;
  let locationTheme = "";

  // Logic for handling location display based on season selection
  if (currentSeason && SEASON_MAP[currentSeason]) {
    // Case 1: Specific Season Selected (e.g. "Spring")
    const seasonKey = SEASON_MAP[currentSeason];
    locationTheme = seasonKey; // Force all locations to match the selected season theme
    
    if (fish.locationDetails && fish.locationDetails[seasonKey] && fish.locationDetails[seasonKey].length > 0) {
        displayLocationList = fish.locationDetails[seasonKey];
    }
  } else {
    // Case 2: "All Seasons" / "Any Season" / Default View
    // We want to color-code locations that are exclusive to a single season.
    // If a location appears in multiple seasons, it stays default (gray).
    
    if (fish.locationDetails) {
        // Calculate season exclusivity for each location
        const locSeasonMap = {}; // { "Beach": ["spring", "summer"] }
        
        ["spring", "summer", "fall", "winter"].forEach(s => {
            const locs = fish.locationDetails[s] || [];
            locs.forEach(loc => {
                if (!locSeasonMap[loc]) locSeasonMap[loc] = [];
                if (!locSeasonMap[loc].includes(s)) locSeasonMap[loc].push(s);
            });
        });

        // Transform displayLocationList into objects with theme info
        // displayLocationList is currently just strings e.g. ["Beach", "Mountain"]
        // We need to map it to [{text: "Beach", theme: ""}, {text: "Mountain", theme: "spring"}]
        
        displayLocationList = displayLocationList.map(locName => {
            const seasons = locSeasonMap[locName];
            let theme = "";
            if (seasons && seasons.length === 1) {
                // Exclusive to one season -> apply that season's color
                theme = seasons[0];
            }
            return { text: locName, theme: theme };
        });
    }
  }

  const legendaryBadge = fish.isLegendary ? `<div class="legendary-tag">👑 传说鱼</div>` : "";

  card.innerHTML = `
    ${legendaryBadge}
    ${image}
    <div class="title-line">
      <div>
        <h2>${escapeHtml(fish.name || "未知鱼类")}</h2>
        ${
          fish.description
            ? `<p class="desc">${formatMultiline(fish.description)}</p>`
            : ""
        }
      </div>
    </div>
    <div class="info-grid">
      ${renderPriceField("基础价格", fish.price)}
      ${renderPriceField("渔夫职业（+25%）", fish.fisherBonus)}
      ${renderPriceField("垂钓者职业（+50%）", fish.anglerBonus)}
      ${renderField("位置", displayLocationList.length ? displayLocationList : fish.location, { asChips: true, chipTheme: locationTheme })}
      ${renderField("时间", fish.time)}
      ${renderField("季节", fish.seasonList, { asChips: true })}
      ${renderField("天气", fish.weatherList, { asChips: true })}
      ${renderField("来源", fish.source, { asChips: true })}
    </div>
  `;
  return card;
}

function renderResults(list, term, hasFilters, currentSeason) {
  const hasSearch = Boolean(term);
  if (!hasSearch && !hasFilters) {
    updateStatus(baseStatus);
  } else {
    updateStatus(`找到 ${list.length} 条匹配结果`);
  }

  if (list.length === 0) {
    renderEmptyHint("没有符合条件的鱼类，尝试调整搜索或筛选条件。");
    return;
  }

  const frag = document.createDocumentFragment();
  list.forEach((fish) => frag.appendChild(createCard(fish, currentSeason)));
  resultsBox.innerHTML = "";
  resultsBox.appendChild(frag);
}

function handleSearch() {
  updateResults();
}

const DATA_FILES = [
  "./data/fish_data.json",
  "./data/ridgeside_fish_data.json",
  "./data/sve_fish_data.json",
  "./data/eastscarp_fish_data.json",
  "./data/mnf_fish_data.json",
  "./data/mtvapius_fish_data.json",
  "./data/dtz_fish_data.json",
  "./data/sbvcp_fish_data.json",
];

async function loadFishData() {
  const responses = await Promise.all(
    DATA_FILES.map((url) => fetch(url, { cache: "no-store" }))
  );
  responses.forEach((response, index) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} (${DATA_FILES[index]})`);
    }
  });
  const payloads = await Promise.all(responses.map((response) => response.json()));
  return payloads.flat();
}

async function init() {
  if (searchInput) searchInput.disabled = true;
  if (weatherFilter) weatherFilter.disabled = true;
  if (seasonFilter) seasonFilter.disabled = true;
  if (sourceFilter) sourceFilter.disabled = true;
  try {
    const raw = await loadFishData();
    fishes = raw.map(buildFishEntity);
    setBaseStatus(`共收录 ${fishes.length} 种鱼类。支持输入空格分隔多个关键词。`);
    populateFilterOptions();
    if (searchInput) {
      searchInput.disabled = false;
      searchInput.focus();
      searchInput.addEventListener("input", handleSearch);
    }
    if (weatherFilter) {
      weatherFilter.disabled = false;
      weatherFilter.addEventListener("change", updateResults);
    }
    if (seasonFilter) {
      seasonFilter.disabled = false;
      seasonFilter.addEventListener("change", updateResults);
    }
    if (sourceFilter) {
      sourceFilter.disabled = false;
      sourceFilter.addEventListener("change", updateResults);
    }
    updateResults();
  } catch (err) {
    console.error("加载鱼类数据失败", err);
    updateStatus("加载鱼类数据失败，请确认数据文件存在。");
    renderEmptyHint("暂时无法读取鱼类数据。");
  }
}

init();
