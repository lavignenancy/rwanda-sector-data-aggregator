import { chromium } from "playwright";

export async function fetchRenderedHtml(url: string): Promise<string> {
  const browser = await chromium.launch({
    headless: true
  });

  try {
    const page = await browser.newPage({
      userAgent: "SectorRwandaAggregator/1.0",
      viewport: {
        width: 1366,
        height: 768
      }
    });

    const response = await page.goto(url, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });

    if (!response || !response.ok()) {
      throw new Error(
        `Failed to load page: ${response?.status() ?? "unknown"}`
      );
    }

    await page.locator(".record").first().waitFor({
      state: "attached",
      timeout: 15000
    });

    return await page.content();
  } finally {
    await browser.close();
  }
}