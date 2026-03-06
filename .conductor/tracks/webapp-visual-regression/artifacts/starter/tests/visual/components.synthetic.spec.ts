import { expect, test } from "@playwright/test";
import { prepareDeterministicPage, waitForStableRender } from "./helpers/deterministic";

test.describe("components visual synthetic", () => {
  test.use({ viewport: { width: 1280, height: 900 } });

  test("button and card primitives", async ({ page }) => {
    await page.setContent(`
      <style>
        body { margin: 0; font-family: "Segoe UI", sans-serif; background: #f8fafc; }
        main { padding: 40px; }
        .row { display: flex; gap: 16px; margin-bottom: 24px; }
        .btn { border: 0; border-radius: 10px; padding: 12px 18px; font-weight: 600; }
        .btn-primary { background: #0f172a; color: #f8fafc; }
        .btn-secondary { background: #dbeafe; color: #1e3a8a; }
        .cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
        .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; min-height: 150px; }
        .card h3 { margin: 0 0 10px; color: #0f172a; }
        .card p { margin: 0; color: #334155; line-height: 1.4; }
      </style>
      <main>
        <div class="row">
          <button class="btn btn-primary">Primary Action</button>
          <button class="btn btn-secondary">Secondary Action</button>
        </div>
        <section class="cards">
          <article class="card"><h3>Card A</h3><p>Delivery confidence and stable quality checks.</p></article>
          <article class="card"><h3>Card B</h3><p>Cross-browser rollout with controlled baseline governance.</p></article>
          <article class="card"><h3>Card C</h3><p>Layout and contrast guardrails for core experiences.</p></article>
        </section>
      </main>
    `);

    await prepareDeterministicPage(page);
    await waitForStableRender(page, "main");
    await expect(page).toHaveScreenshot("components-primitives-desktop.png", { fullPage: false });
  });

  test("form field stack", async ({ page }) => {
    await page.setContent(`
      <style>
        body { margin: 0; font-family: "Segoe UI", sans-serif; background: #f1f5f9; }
        .shell { max-width: 680px; margin: 48px auto; background: #fff; border-radius: 16px; border: 1px solid #dbe3ef; padding: 24px; }
        h2 { margin: 0 0 14px; color: #0f172a; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .field { display: flex; flex-direction: column; gap: 8px; }
        .field label { color: #334155; font-size: 14px; }
        .field input, .field textarea { border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px 12px; font-size: 14px; }
        .field textarea { min-height: 120px; resize: vertical; }
      </style>
      <main class="shell">
        <h2>Contact Form Primitive</h2>
        <div class="grid">
          <div class="field"><label>Name</label><input value="Avery Jordan" /></div>
          <div class="field"><label>Email</label><input value="avery@example.com" /></div>
        </div>
        <div class="field" style="margin-top: 14px;"><label>Message</label><textarea>Confirm release readiness and baseline rationale.</textarea></div>
      </main>
    `);

    await prepareDeterministicPage(page);
    await waitForStableRender(page, ".shell");
    await expect(page).toHaveScreenshot("components-form-desktop.png", { fullPage: false });
  });
});
