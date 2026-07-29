import fs from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const entries = await fs.readdir(root, { withFileTypes: true });
let updated = 0;

for (const entry of entries) {
  if (!entry.isFile() || !entry.name.endsWith(".html")) continue;

  const filePath = path.join(root, entry.name);
  const original = await fs.readFile(filePath, "utf8");
  if (original.includes('href="palais-vet.css"')) continue;

  const needle = '</head>';
  if (!original.includes(needle)) {
    throw new Error(`Missing </head> in ${entry.name}`);
  }

  const updatedHtml = original.replace(
    needle,
    '  <link rel="stylesheet" href="palais-vet.css">\n' + needle,
  );
  await fs.writeFile(filePath, updatedHtml, "utf8");
  updated += 1;
}

console.log(`Updated ${updated} HTML files.`);
