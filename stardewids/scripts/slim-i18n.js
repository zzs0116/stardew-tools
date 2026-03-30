#!/usr/bin/env node
// slim-i18n.js (ESM 版本)：保留中文/英文，输出到 public/dist_slim
import fs from 'node:fs';
import path from 'node:path';

const SRC_DIR = process.argv[2] || path.join(process.cwd(), 'public', 'dist');
const OUT_DIR = process.argv[3] || path.join(process.cwd(), 'public', 'dist_slim');

if (!fs.existsSync(SRC_DIR)) {
  console.error(`❌ 源目录不存在：${SRC_DIR}`);
  process.exit(1);
}
fs.mkdirSync(OUT_DIR, { recursive: true });

const EN_NAME_KEYS = ['data-en-US', 'en-US', 'data-en', 'en'];
const ZH_NAME_KEYS = ['data-zh-CN', 'zh-CN', 'data-zh', 'zh'];
const EN_TRANS_KEYS = ['en', 'en-US'];
const ZH_TRANS_KEYS = ['zh', 'zh-CN'];

function pickFirst(o, keys) {
  for (const k of keys) {
    if (o && Object.prototype.hasOwnProperty.call(o, k)) {
      const v = o[k];
      if (v !== undefined && v !== null && String(v).trim() !== '') return String(v);
    }
  }
  return undefined;
}

function slimNode(node) {
  if (Array.isArray(node)) return node.map(slimNode);
  if (node && typeof node === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(node)) {
      if (k === 'names' && v && typeof v === 'object' && !Array.isArray(v)) {
        const en = pickFirst(v, EN_NAME_KEYS);
        const zh = pickFirst(v, ZH_NAME_KEYS);
        const nv = {};
        if (en !== undefined) nv['data-en-US'] = en;
        if (zh !== undefined) nv['data-zh-CN'] = zh;
        out[k] = nv;
      } else if (k === 'translations' && v && typeof v === 'object' && !Array.isArray(v)) {
        const en = pickFirst(v, EN_TRANS_KEYS);
        const zh = pickFirst(v, ZH_TRANS_KEYS);
        const nv = {};
        if (en !== undefined) nv['en'] = en;
        if (zh !== undefined) nv['zh'] = zh;
        out[k] = nv;
      } else {
        out[k] = slimNode(v);
      }
    }
    return out;
  }
  return node;
}

function readJSON(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(raw);
}
function writeJSON(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
}

const files = fs.readdirSync(SRC_DIR).filter(f => f.endsWith('.json'));

let totalIn = 0, totalOut = 0;
for (const f of files) {
  const src = path.join(SRC_DIR, f);
  const dst = path.join(OUT_DIR, f);
  try {
    const json = readJSON(src);
    const isArrayTop = Array.isArray(json);
    let entries;

    if (isArrayTop) {
      entries = json.map(v => ({ _k: undefined, _v: v }));
    } else if (json && typeof json === 'object') {
      entries = Object.entries(json).map(([k, v]) => ({ _k: k, _v: v }));
    } else {
      console.warn(`! 跳过（顶层不是对象或数组）：${f}`);
      continue;
    }

    totalIn += entries.length;
    const slimmedEntries = entries.map(({ _k, _v }) => ({ _k, _v: slimNode(_v) }));

    let outJson;
    if (isArrayTop) {
      outJson = slimmedEntries.map(e => e._v);
    } else {
      outJson = {};
      for (const { _k, _v } of slimmedEntries) outJson[_k] = _v;
    }

    writeJSON(dst, outJson);
    totalOut += slimmedEntries.length;
    console.log(`✓ ${f}  ->  ${path.relative(process.cwd(), dst)}  (${slimmedEntries.length} items)`);
  } catch (e) {
    console.error(`✗ 处理失败：${f}\n   ${e.message}`);
  }
}

console.log(`\n✅ 完成。输入条目：${totalIn}，输出条目：${totalOut}`);
console.log(`📁 输出目录：${OUT_DIR}`);