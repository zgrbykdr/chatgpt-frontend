const path = require('path');

function normalizeHeader(v) {
  return v.toLowerCase().replace(/[^a-z]/g, '');
}

function splitRow(row) {
  if (row.includes('\t')) return row.split('\t').map((x) => x.trim());
  return row.split(/\s{2,}/).map((x) => x.trim());
}

function parseFeatTxt(raw, filePath = 'import.txt') {
  const lines = raw
    .replace(/^\uFEFF/, '')
    .split(/\r?\n/)
    .map((l) => l.trimEnd())
    .filter((l) => l.trim().length > 0);
  if (lines.length < 2) return { sourceFile: filePath, rows: [], errors: ['No data rows found.'] };

  const headerCols = splitRow(lines[0]);
  const norm = headerCols.map(normalizeHeader);
  const nameIdx = norm.findIndex((h) => h.includes('name'));
  const sourceIdx = norm.findIndex((h) => h.includes('source'));
  const descIdx = norm.findIndex((h) => h.includes('description') || h.includes('summary') || h.includes('desc'));

  const rows = [];
  const errors = [];
  const dedupe = new Set();
  for (let i = 1; i < lines.length; i += 1) {
    const cols = splitRow(lines[i]);
    const name = cols[nameIdx >= 0 ? nameIdx : 0] || '';
    const source = cols[sourceIdx >= 0 ? sourceIdx : 1] || 'Unknown Source';
    const summary = cols[descIdx >= 0 ? descIdx : 2] || '';

    if (!name) {
      errors.push(`Row ${i + 1}: missing feat name`);
      continue;
    }
    const key = `${name.toLowerCase()}|${source.toLowerCase()}`;
    if (dedupe.has(key)) continue;
    dedupe.add(key);

    rows.push({
      id: `imported_${name.toLowerCase().replace(/[^a-z0-9]+/g, '_')}_${i}`,
      name,
      source,
      summary,
      mappingStatus: 'Unmapped',
      importedFrom: path.basename(filePath),
    });
  }

  return { sourceFile: filePath, rows, errors };
}

module.exports = { parseFeatTxt };
