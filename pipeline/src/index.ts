import { readFile } from "node:fs/promises";
import { extractRecords } from "./scraper.js";
import { processRecord, deduplicate } from "./processor.js";

async function fetchWithRetry(
  url: string,
  attempts = 3
): Promise<string> {
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      const response = await fetch(url, {
        headers: {
          "User-Agent": "SectorRwandaAggregator/1.0"
        },
        signal: AbortSignal.timeout(15000)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.text();
    } catch (error) {
      if (attempt === attempts) {
        throw error;
      }

      await new Promise((resolve) =>
        setTimeout(resolve, 1000 * 2 ** (attempt - 1))
      );
    }
  }

  throw new Error("Unable to fetch source");
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const fixtureIndex = args.indexOf("--fixture");

  let html: string;
  let sourceUrl: string;

  if (fixtureIndex !== -1) {
    const file = args[fixtureIndex + 1];

    if (!file) {
      throw new Error("Provide a fixture file path");
    }

    html = await readFile(file, "utf8");
    sourceUrl = "https://example.org/demo";
  } else {
    const url = args[0];

    if (!url || !/^https?:\/\//i.test(url)) {
      throw new Error("Provide a valid public source URL");
    }

    const parsed = new URL(url);

    if (
      parsed.protocol !== "https:" ||
      parsed.username ||
      parsed.password
    ) {
      throw new Error("Only public HTTPS URLs are supported");
    }

    sourceUrl = parsed.toString();
    html = await fetchWithRetry(sourceUrl);
  }

  const extracted = extractRecords(html, sourceUrl);
  const processed = extracted.map(processRecord);
  const unique = deduplicate(processed);

  console.log(
    JSON.stringify(
      {
        source: sourceUrl,
        extracted: extracted.length,
        duplicates: processed.length - unique.length,
        records: unique
      },
      null,
      2
    )
  );
}

main().catch((error: unknown) => {
  console.error(
    error instanceof Error ? error.message : "Pipeline failed"
  );
  process.exitCode = 1;
});