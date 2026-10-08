export interface SectorMetricPayload {
  population?: number;
  poverty_rate?: number;
  literacy_rate?: number;
  access_to_electricity?: number;
  [key: string]: any;
}

export interface SectorDataNode {
  id: number;
  sector: string;
  data_type: string;
  source_url: string;
  structural_signature: string;
  payload: SectorMetricPayload;
  created_at: string;
  updated_at: string;
}

export interface SyncResponse {
  status: string;
  task_id: string;
  message: string;
}
