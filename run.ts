import * as fs from 'fs';
import * as path from 'path';
import { harvestSectorData } from './app/scraper';
import { ChangeDetectionEngine } from './app/classifier';
import { SectorRecord } from './app/types';

async function executePipeline(): Promise<void> {
  const targetSources: string[] = [
    'https://weworkremotely.com/remote-jobs.rss'
  ];

  const currentScrapedRecords = await harvestSectorData(targetSources);
  const engine = new ChangeDetectionEngine();
  
  const historyFilePath = path.join(__dirname, 'output_jobs.json');
  let historicalRecords: SectorRecord[] = [];
  
  if (fs.existsSync(historyFilePath)) {
    try {
      const fileContent = fs.readFileSync(historyFilePath, 'utf-8');
      historicalRecords = JSON.parse(fileContent);
      engine.registerHistoricalStates(historicalRecords);
    } catch (e) {
      historicalRecords = [];
    }
  }

  const finalizedOutput: SectorRecord[] = [...historicalRecords];
  
  for (const record of currentScrapedRecords) {
    const evaluation = engine.evaluateCurrentState(record);
    
    const isAlreadySaved = finalizedOutput.some(r => r.sector_id === record.sector_id);
    
    if (evaluation.has_changed || !isAlreadySaved) {
      if (isAlreadySaved) {
        const targetIndex = finalizedOutput.findIndex(r => r.sector_id === record.sector_id);
        finalizedOutput[targetIndex] = record;
      } else {
        finalizedOutput.push(record);
      }
    }
  }

  fs.writeFileSync(historyFilePath, JSON.stringify(finalizedOutput, null, 2), 'utf-8');
}

executePipeline();
