import { Platform } from 'react-native';
import { Alert, Dashboard, Reading, Recommendation, Region, RiskResponse, Sensor } from '../types';

export const isDemoMode = process.env.EXPO_PUBLIC_DATA_MODE === 'demo';
const apiBase = (process.env.EXPO_PUBLIC_API_BASE_URL ?? '').trim().replace(/\/+$/, '');

async function get<T>(path: string): Promise<T> {
  if (Platform.OS !== 'web' && !apiBase) {
    throw new Error('Configure EXPO_PUBLIC_API_BASE_URL para acessar a API no dispositivo.');
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch(`${apiBase}/api/${path}`, { signal: controller.signal });
    if (!response.ok) throw new Error(`API respondeu HTTP ${response.status} (${path}).`);
    return await response.json() as T;
  } catch (error) {
    if (controller.signal.aborted) throw new Error('Tempo limite ao consultar a API.');
    if (error instanceof TypeError) throw new Error('Não foi possível alcançar a API.');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function getList<T>(path: string): Promise<T[]> {
  const payload = await get<T[]>(path);
  if (!Array.isArray(payload)) throw new Error(`Resposta inesperada da API (${path}).`);
  return payload;
}

export async function fetchDashboard(): Promise<Dashboard> {
  type RemoteAlert = Omit<Alert, 'reason'> & { description: string };
  const [regions, sensors, readings, rawAlerts, risks] = await Promise.all([
    getList<Omit<Region, 'sensorsCount'>>('regions'),
    getList<Sensor>('sensors'),
    getList<Reading>('readings/latest'),
    getList<RemoteAlert>('alerts/active'),
    getList<RiskResponse>('risk'),
  ]);
  const sensorCounts = new Map<number, number>();
  for (const sensor of sensors) {
    sensorCounts.set(sensor.regionId, (sensorCounts.get(sensor.regionId) ?? 0) + 1);
  }
  return {
    regions: regions.map(region => ({ ...region, sensorsCount: sensorCounts.get(region.id) ?? 0 })),
    alerts: rawAlerts.map(alert => ({ ...alert, reason: alert.description })),
    sensors,
    readings,
    risks,
  };
}

export function fetchRecommendation(regionId: number): Promise<Recommendation> {
  return get<Recommendation>(`recommendations/regions/${regionId}`);
}
