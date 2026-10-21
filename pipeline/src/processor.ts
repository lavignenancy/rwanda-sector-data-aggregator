import { createHash } from "node:crypto";
import type { SectorRecord } from "./scraper.js";

export interface ProcessedRecord extends SectorRecord {
  fingerprint: string;
}

export function sanitize(value: string): string {
  return value
    .replace(/<[^>]*>/g, "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function processRecord(
  record: SectorRecord
): ProcessedRecord {
  const cleaned: SectorRecord = {
    name: sanitize(record.name),
    sector: sanitize(record.sector),
    district: sanitize(record.district),
    province: sanitize(record.province),
    sourceUrl: record.sourceUrl.trim()
  };

  const fingerprint = createHash("sha256")
    .update(
      JSON.stringify([
        cleaned.name.toLowerCase(),
        cleaned.sector.toLowerCase(),
        cleaned.district.toLowerCase(),
        cleaned.province.toLowerCase()
      ])
    )
    .digest("hex");

  return {
    ...cleaned,
    fingerprint
  };
}

export function deduplicate(
  records: ProcessedRecord[]
): ProcessedRecord[] {
  const seen = new Set<string>();

  return records.filter((record) => {
    if (seen.has(record.fingerprint)) {
      return false;
    }

    seen.add(record.fingerprint);
    return true;
  });
}