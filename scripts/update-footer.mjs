import { readdir, readFile, writeFile } from "node:fs/promises";

const footer = `    <footer class="concept-footer">
      <div class="concept-shell concept-footer-grid">
        <div>
          <p class="concept-footer-title">Ветеринар на связи</p>
          <p class="concept-footer-address">г. Раменское,<br>ул. Красноармейская, д. 13Б</p>
          <a class="concept-footer-phone" href="tel:+74951444803">+7 (495) 144-48-03</a>
        </div>
        <nav class="concept-footer-nav" aria-label="Навигация в подвале">
          <a href="index.html">Главная</a>
          <a href="o-kompanii.html">О компании</a>
          <a href="uslugi-i-tseny.html">Услуги и цены</a>
          <a href="vakansii.html">Вакансии</a>
          <a href="novosti.html">Новости</a>
          <a href="index.html#contacts">Контакты</a>
        </nav>
        <div class="concept-footer-legal">
          <div>
            <p class="concept-footer-label">Клиника</p>
            <p class="concept-footer-address">Приём животных ежедневно.<br>Уточните удобное время по телефону.</p>
          </div>
          <a href="politika-konfidencialnosti.html">Политика конфиденциальности</a>
        </div>
      </div>
      <div class="concept-shell">
        <p class="concept-footer-copy">© 2026 Ветеринар на связи</p>
      </div>
    </footer>`;

const files = (await readdir(".")).filter((file) => file.endsWith(".html"));
let updated = 0;

for (const file of files) {
  const source = await readFile(file, "utf8");
  if (!source.includes('<footer class="concept-footer">')) {
    continue;
  }

  const next = source.replace(/    <footer class="concept-footer">[\s\S]*?    <\/footer>/, footer);
  if (next !== source) {
    await writeFile(file, next);
    updated += 1;
  }
}

console.log(`Updated ${updated} footers.`);
