import { Alert, DashboardMetrics, Region } from '../types';

export const regions: Region[] = [
  { id: 1, name: 'Margem Rio Tietê - Norte', city: 'São Paulo', state: 'SP', riskLevel: 'HIGH', satelliteRiskScore: 82, sensorsCount: 5 },
  { id: 2, name: 'Serra da Mantiqueira - Sul', city: 'Campos do Jordão', state: 'SP', riskLevel: 'MEDIUM', satelliteRiskScore: 68, sensorsCount: 4 },
  { id: 3, name: 'Zona Rural Oeste', city: 'Campinas', state: 'SP', riskLevel: 'CRITICAL', satelliteRiskScore: 91, sensorsCount: 6 },
  { id: 4, name: 'Área de Preservação Leste', city: 'Niterói', state: 'RJ', riskLevel: 'LOW', satelliteRiskScore: 45, sensorsCount: 3 }
];

export const alerts: Alert[] = [
  {
    id: 101,
    title: 'Risco de enchente detectado',
    regionId: 1,
    severity: 'HIGH',
    status: 'OPEN',
    sensorData: 'WATER_LEVEL: 86% | RAINFALL: 63 mm',
    recommendedAction: 'Ativar protocolo municipal de prevenção e notificar população ribeirinha.',
    reason: 'Nível de água e chuva ultrapassaram limiares críticos definidos no MVP.'
  },
  {
    id: 102,
    title: 'Fumaça elevada em área rural',
    regionId: 3,
    severity: 'CRITICAL',
    status: 'MONITORING',
    sensorData: 'SMOKE: 74 | TEMPERATURE: 41°C',
    recommendedAction: 'Acionar monitoramento contínuo e equipe de campo preventiva.',
    reason: 'Índice de fumaça e temperatura sugerem risco de foco de incêndio.'
  }
];

export const dashboardMetrics: DashboardMetrics = {
  activeAlerts: alerts.filter(a => a.status !== 'RESOLVED').length,
  monitoredRegions: regions.length,
  onlineSensors: regions.reduce((acc, r) => acc + r.sensorsCount, 0),
  generalRisk: 'HIGH'
};
