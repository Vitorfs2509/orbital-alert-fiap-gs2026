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
  sensorData: string;
  recommendedAction: string;
  reason: string;
};

export type DashboardMetrics = {
  activeAlerts: number;
  monitoredRegions: number;
  onlineSensors: number;
  generalRisk: RiskLevel;
};
