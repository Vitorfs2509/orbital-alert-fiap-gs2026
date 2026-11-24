export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertStatus = 'OPEN' | 'MONITORING' | 'RESOLVED';

export type Region = {
  id: number;
  name: string;
  city: string;
  state: string;
  riskLevel: RiskLevel;
  satelliteRiskScore: number;
  sensorsCount: number;
};

export type Alert = {
  id: number;
  title: string;
  regionId: number;
  severity: RiskLevel;
  status: AlertStatus;
  sensorData?: string;
  recommendedAction?: string;
  createdAt?: string;
  reason: string;
};

export type Sensor = {
  id: number;
  regionId: number;
  type: string;
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE';
  unit: string;
};

export type Reading = {
  id: number;
  sensorId: number;
  value: number;
  measuredAt: string;
};

export type RegionRisk = {
  regionId: number;
  riskScore: number;
  riskLevel: RiskLevel;
  riskType: string;
  readings: number;
  generatedAt: string;
  indicators: {
    sensorType: string;
    lastValue: number;
    avgValue: number;
    unit: string;
    subScore: number;
  }[];
};

export type RiskResponse = {
  dataSource: 'CURATED_LAYER' | 'OPERATIONAL_DB_FALLBACK';
  context: RegionRisk;
};

export type Recommendation = {
  recommendation: string;
  aiMode: string;
  dataSource: RiskResponse['dataSource'];
  generatedAt: string;
};

export type Dashboard = {
  regions: Region[];
  alerts: Alert[];
  sensors: Sensor[];
  readings: Reading[];
  risks: RiskResponse[];
};

export type DashboardMetrics = {
  activeAlerts: number;
  monitoredRegions: number;
  onlineSensors: number;
  generalRisk: RiskLevel;
};
