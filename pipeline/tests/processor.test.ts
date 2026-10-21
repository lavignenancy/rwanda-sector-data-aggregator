import {
  sanitize,
  processRecord,
  deduplicate
} from "../src/processor.js";

const record = {
  name: "Example Cooperative",
  sector: "Agriculture",
  district: "Gasabo",
  province: "Kigali",
  sourceUrl: "https://example.org"
};

describe("Data processing", () => {
  test("removes HTML tags and normalizes whitespace", () => {
    expect(sanitize("  <b>Example</b>   Cooperative  "))
      .toBe("Example Cooperative");
  });

  test("generates deterministic fingerprints", () => {
    const first = processRecord(record);
    const second = processRecord(record);

    expect(first.fingerprint).toBe(second.fingerprint);
    expect(first.fingerprint).toHaveLength(64);
  });

  test("detects changes to record content", () => {
    const first = processRecord(record);
    const second = processRecord({
      ...record,
      district: "Kicukiro"
    });

    expect(first.fingerprint).not.toBe(second.fingerprint);
  });

  test("removes duplicate records", () => {
    const records = [
      processRecord(record),
      processRecord(record),
      processRecord({
        ...record,
        name: "Another Cooperative"
      })
    ];

    expect(deduplicate(records)).toHaveLength(2);
  });
});