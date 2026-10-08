export interface SectorRecord {
  sector_id: string;
  category: string;
  region: string;
  metrics: {
    summary: string;
    source_length: number;
  };
  data_hash: string;
  last_updated: string;
}

export interface ChangeLogResult {
  sector_id: string;
  has_changed: boolean;
  old_hash: string | null;
  new_hash: string;
  detected_at: string;
}
