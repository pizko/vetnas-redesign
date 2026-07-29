import { readdir, readFile, writeFile } from "node:fs/promises";

const link = '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600;700;800&display=swap">\n';
const files = (await readdir(".")).filter((file) => file.endsWith(".html"));
let updated = 0;

for (const file of files) {
  const source = await readFile(file, "utf8");
  if (source.includes("family=Unbounded")) continue;
  if (!source.includes("</head>")) throw new Error(`Missing head: ${file}`);
  await writeFile(file, source.replace("</head>", `${link}</head>`));
  updated += 1;
}

console.log(`Updated ${updated} HTML files.`);
