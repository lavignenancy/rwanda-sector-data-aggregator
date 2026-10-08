<<<<<<< HEAD
import { SectorRecord, ChangeLogResult } from './types';

export class ChangeDetectionEngine {
  private stateRegistry: Map<string, string>;

  constructor() {
    this.stateRegistry = new Map<string, string>();
  }

  public registerHistoricalStates(historicalRecords: SectorRecord[]): void {
    for (const record of historicalRecords) {
      this.stateRegistry.set(record.sector_id, record.data_hash);
    }
  }

  public evaluateCurrentState(currentRecord: SectorRecord): ChangeLogResult {
    const sectorId = currentRecord.sector_id;
    const oldHash = this.stateRegistry.get(sectorId) || null;
    const newHash = currentRecord.data_hash;
    
    const hasChanged = oldHash !== newHash;
    
    if (hasChanged) {
      this.stateRegistry.set(sectorId, newHash);
    }

    return {
      sector_id: sectorId,
      has_changed: hasChanged,
      old_hash: oldHash,
      new_hash: newHash,
      detected_at: new Date().toISOString()
=======
import axios from 'axios';
import { Job } from './scraper';

export interface ProcessedJob extends Job {
  skills: string[];
  seniority: 'Intern' | 'Junior' | 'Mid' | 'Senior' | 'Lead' | 'Unknown';
}

export async function classifyJobDescription(job: Job, apiKey: string): Promise<ProcessedJob> {
  try {
    const response = await axios.post(
      'https://openai.com',
      {
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: 'Extract the technical keys from the text. Return valid JSON containing two attributes: "skills" (array of strings) and "seniority" (strictly choose one: Intern, Junior, Mid, Senior, Lead, Unknown).'
          },
          {
            role: 'user',
            content: `Title: ${job.title}\nDescription: ${job.description}`
          }
        ],
        response_format: { type: 'json_object' },
        temperature: 0.1
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const parsedIntelligence = JSON.parse(response.data.choices[0].message.content);
    
    return {
      ...job,
      skills: Array.isArray(parsedIntelligence.skills) ? parsedIntelligence.skills : [],
      seniority: parsedIntelligence.seniority || 'Unknown'
    };
  } catch (error) {
    return {
      ...job,
      skills: [],
      seniority: 'Unknown'
>>>>>>> 2794326 (Scaled up data layer to postgres and integrate async celery architecture)
    };
  }
}
