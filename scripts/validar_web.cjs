// Smoke test do painel exportado. Requer playwright-core e um Chromium já instalado.
const { chromium } = require('playwright-core');
const fs = require('node:fs/promises');
const path = require('node:path');

async function verify() {
  const [phase, evidencePath, demoPath] = process.argv.slice(2);
  if (!['empty', 'populated', 'unavailable'].includes(phase) || !evidencePath) {
    throw new Error('Uso: node scripts/validar_web.cjs empty|populated|unavailable PASTA [DEMO_JSON]');
  }
  const url = process.env.ORBITAL_WEB_URL || 'http://localhost:8080/';
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE || undefined,
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1180, height: 920 } });
  page.setDefaultTimeout(12000);
  const checks = [];
  const responses = [];
  page.on('response', response => {
    if (new URL(response.url()).pathname.startsWith('/api/')) {
      responses.push({ path: new URL(response.url()).pathname, status: response.status() });
    }
  });
  async function see(text) {
    await page.getByText(text, { exact: typeof text === 'string' }).first().waitFor({ state: 'visible' });
    checks.push(String(text));
  }
  async function screenshot(suffix) {
    await page.screenshot({ path: path.join(evidencePath, `web-${suffix}.png`) });
  }
  try {
    await fs.mkdir(evidencePath, { recursive: true });
    const response = await page.goto(url, { waitUntil: 'domcontentloaded' });
    if (!response?.ok()) throw new Error('Frontend não respondeu.');
    await page.getByRole('button', { name: 'Abrir painel' }).click();
    if (phase === 'empty') {
      await see('Nenhuma região cadastrada.');
      await see('Nenhum alerta ativo.');
      await screenshot('vazio');
    } else if (phase === 'unavailable') {
      await see('Falha de integração');
      if (await page.getByText('Margem Rio Tietê - Norte', { exact: true }).count()) {
        throw new Error('O painel voltou para dados mock por engano.');
      }
      await screenshot('indisponivel');
    } else {
      const recorded = await fs.readFile(demoPath, 'utf8');
      const run = JSON.parse(recorded.replace(/^\uFEFF/, ''));
      const { riskScore } = run.risk.context;
      await see(run.region.name);
      await see(new RegExp(`Risk Score IoT: ${riskScore}/100`));
      await see(/Data Lake · CURATED/);
      await screenshot('dashboard');
      await page.getByText(run.region.name, { exact: true }).click();
      await see(new RegExp(`leitura #${run.readings.at(-1).id} ·`));
      await see(new RegExp(`Alerta #${run.alert.id} ·`));
      await see('Indicadores de risco');
      if (run.recommendation) {
        await page.getByRole('button', { name: 'Consultar recomendação' }).click();
        await see('Recomendação consultiva');
        await see(new RegExp(`^${run.recommendation.aiMode} · Data Lake · CURATED`));
      }
      await screenshot('regiao');
    }
    console.log(JSON.stringify({ phase, atUtc: new Date().toISOString(), checks, responses }, null, 2));
  } finally {
    await browser.close();
  }
}

verify().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
