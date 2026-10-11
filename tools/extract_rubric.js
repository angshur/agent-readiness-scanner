// Extracts CATEGORIES and QUESTIONS from web/index.html into rubric.json,
// so the Python scorer and the web demo share one rubric.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const start = html.indexOf("var CATEGORIES");
const end = html.indexOf("var STORAGE_ANSWERS");
const { CATEGORIES, QUESTIONS } = new Function(
  html.slice(start, end) + "; return {CATEGORIES: CATEGORIES, QUESTIONS: QUESTIONS};"
)();
const out = {
  categories: CATEGORIES.map(c => ({ id: c.id, name: c.name, weight: c.weight })),
  bands: [
    { min: 80, label: "Agent-Ready" },
    { min: 60, label: "Partially Ready" },
    { min: 35, label: "Significant Gaps" },
    { min: 0, label: "Not Agent-Ready" }
  ],
  questions: QUESTIONS.map(q => ({
    id: q.id, category: q.category, text: q.text,
    options: q.options.map(o => ({ label: o.label, score: o.score, gap: o.gap || null }))
  }))
};
process.stdout.write(JSON.stringify(out, null, 2) + "\n");
