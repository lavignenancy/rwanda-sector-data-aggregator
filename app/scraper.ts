import axios from 'axios';
import * as cheerio from 'cheerio';
import { SectorRecord } from './types';

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

export function cleanUnstructuredText(rawText: string): string {
  let cleaned = rawText.replace(/(system override|ignore previous instructions|act as admin|bypass)/gi, '[REDACTED_GUARDRAIL]');
  cleaned = cleaned.replace(/[<>{}▪\\^`]/g, '');
  return cleaned.trim();
}

export function generateFingerprint(data: Record<string, any>): string {
  const serialized = Object.keys(data)
    .sort()
    .map(key => `${key}:${data[key]}`)
    .join('|');
    
  let hash = 0;
  for (let i = 0; i < serialized.length; i++) {
    const chr = serialized.charCodeAt(i);
    hash = ((hash << 5) - hash) + chr;
    hash |= 0;
  }
  return Math.abs(hash).toString(16);
}

export async function harvestSectorData(sources: string[]): Promise<SectorRecord[]> {
  const gatheredRecords: SectorRecord[] = [];
  const seenSignatures = new Set<string>();

  for (const sourceUrl of sources) {
    try {
      const response = await axios.get(sourceUrl, {
        headers: { 'User-Agent': 'RwandaSectorDataAggregator/1.0' }
      });
      
           const $ = cheerio.load(response.data, { xmlMode: true });
      $('item').each((_, element) => {
        const sector_id = $(element).find('guid').text().trim() || Math.random().toString(36).substring(2, 9);
        const category = $(element).find('category').text().trim() || 'General Development';
        const region = $(element).find('title').text().trim() || 'Regional Data Node';
        const rawSummary = $(element).find('description').text().replace(/<[^>]*>/g, '').trim();

        
        const cleanedSummary = cleanUnstructuredText(rawSummary);
        
        const metrics = {
          summary: cleanedSummary.substring(0, 300),
          source_length: cleanedSummary.length
        };
        
        const fingerprint = generateFingerprint(metrics);
        
        if (!seenSignatures.has(fingerprint)) {
          seenSignatures.add(fingerprint);
          gatheredRecords.push({
            sector_id,
            category,
            region,
            metrics,
            data_hash: fingerprint,
            last_updated: new Date().toISOString()
          });
        }
      });
      
      await sleep(1000);
    } catch (error) {
      continue;
    }
  }

  return gatheredRecords;
}
