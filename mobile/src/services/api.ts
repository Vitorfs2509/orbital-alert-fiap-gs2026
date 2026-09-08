import { Alert, AlertStatus, RiskLevel } from '../types';

/**
 * Integração opcional com o backend real.
 *
 * Quando `EXPO_PUBLIC_API_BASE_URL` está definida, o app busca os alertas em
 * `GET /api/alerts`. Sem a variável — ou se a API não responder — o app
 * continua usando os dados mockados de `src/data/mockData.ts`, para que a
 * demonstração offline nunca quebre.
 */

const RAW_BASE_URL = (process.env.EXPO_PUBLIC_API_BASE_URL ?? '').trim();

/** Base da API sem a barra final (ex.: `http://192.168.0.10:8080`). */
export const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

/** `true` apenas quando o app foi configurado para falar com um backend. */
export const isBackendConfigured = API_BASE_URL.length > 0;

export type DataSource = 'MOCK' | 'BACKEND';

/** Tempo máximo de espera: uma API fora do ar não pode travar a demonstração. */
const REQUEST_TIMEOUT_MS = 4000;

/** Formato de `AlertDto` no backend Spring Boot. */
type BackendAlert = {
  id: number;
  regionId: number;
  regionName: string | null;
  title: string;
  description: string | null;
  severity: RiskLevel;
  status: AlertStatus;
  createdAt: string | null;
  resolvedAt: string | null;
};

/**
 * O backend não guarda `sensorData` nem `recommendedAction` — esses campos são
 * texto de apoio da tela. Preenchemos com o que o alerta real oferece, mantendo
 * o mesmo tipo `Alert` já usado pela interface.
 */
const toAlert = (dto: BackendAlert): Alert => ({
  id: dto.id,
  title: dto.title,
  regionId: dto.regionId,
  severity: dto.severity,
  status: dto.status,
  sensorData: dto.regionName ? `Região: ${dto.regionName}` : 'Leitura recebida via API',
  recommendedAction: 'Acionar o protocolo preventivo da região e acompanhar as próximas leituras.',
  reason: dto.description ?? 'Alerta gerado pelas regras de limiar do AlertService.'
});

/**
 * Busca os alertas no backend real.
 * Lança erro quando não há API configurada ou quando a chamada falha —
 * quem chama decide o fallback.
 */
export async function fetchAlerts(): Promise<Alert[]> {
  if (!isBackendConfigured) {
    throw new Error('EXPO_PUBLIC_API_BASE_URL não configurada');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/api/alerts`, { signal: controller.signal });
    if (!response.ok) {
      throw new Error(`API respondeu ${response.status}`);
    }

    const payload = (await response.json()) as BackendAlert[];
    if (!Array.isArray(payload)) {
      throw new Error('Resposta inesperada da API');
    }

    return payload.map(toAlert);
  } finally {
    clearTimeout(timeout);
  }
}
