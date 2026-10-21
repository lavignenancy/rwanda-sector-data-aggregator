import * as cheerio from "cheerio";

export interface SectorRecord {
  name: string;
  sector: string;
  district: string;
  province: string;
  sourceUrl: string;
}

export function extractRecords(
  html: string,
  sourceUrl: string
): SectorRecord[] {
  const $ = cheerio.load(html);
  const records: SectorRecord[] = [];

  $(".record").each((_, element) => {
    const name = $(element).find(".name").text().trim();
    const sector = $(element).find(".sector").text().trim();
    const district = $(element).find(".district").text().trim();
    const province = $(element).find(".province").text().trim();

    if (!name || !sector || !district || !province) {
      return;
    }

    records.push({
      name,
      sector,
      district,
      province,
      sourceUrl
    });
  });

  return records;
}