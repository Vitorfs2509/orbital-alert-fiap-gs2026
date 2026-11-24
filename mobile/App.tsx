import React, { useEffect, useMemo, useState } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { alerts as mockAlerts, dashboardMetrics, regions as mockRegions } from './src/data/mockData';
import { MetricCard } from './src/components/MetricCard';
import { fetchDashboard, fetchRecommendation, isDemoMode } from './src/services/api';
import { Dashboard, Recommendation, RiskLevel } from './src/types';
import { colors } from './src/theme/colors';

type Screen = 'welcome' | 'dashboard' | 'regions' | 'details';
type Load<T> = { status: 'loading' } | { status: 'ready'; data: T } | { status: 'error'; message: string };

const mockDashboard: Dashboard = {
  alerts: mockAlerts, regions: mockRegions, sensors: [], readings: [], risks: [],
};
const riskColors = { LOW: colors.low, MEDIUM: colors.medium, HIGH: colors.high, CRITICAL: colors.critical };
const riskLabel = { LOW: 'Baixo', MEDIUM: 'Moderado', HIGH: 'Alto', CRITICAL: 'Crítico' };
const riskSource = { CURATED_LAYER: 'Data Lake · CURATED', OPERATIONAL_DB_FALLBACK: 'Banco operacional' };
const riskRank: RiskLevel[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const message = (error: unknown) => error instanceof Error ? error.message : 'Falha ao carregar os dados.';
const utc = (timestamp: string) => timestamp.replace('T', ' ').replace(/(?:Z|\+00:00)$/, '') + ' UTC';

function Action({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <TouchableOpacity accessibilityRole="button" style={styles.button} onPress={onPress}>
      <Text style={styles.buttonText}>{label}</Text>
    </TouchableOpacity>
  );
}

export default function App() {
  const [screen, setScreen] = useState<Screen>('welcome');
  const [selection, setSelection] = useState<number | null>(null);
  const [load, setLoad] = useState<Load<Dashboard>>({ status: 'loading' });
  const [reload, setReload] = useState(0);
  const [recommendation, setRecommendation] = useState<Load<Recommendation> | null>(null);
  const entered = screen !== 'welcome';

  useEffect(() => {
    if (!entered || isDemoMode) return;
    let active = true;
    fetchDashboard().then(
      data => { if (active) setLoad({ status: 'ready', data }); },
      error => { if (active) setLoad({ status: 'error', message: message(error) }); },
    );
    return () => { active = false; };
  }, [entered, reload]);

  const data = isDemoMode ? mockDashboard : load.status === 'ready' ? load.data : null;
  const riskByRegion = useMemo(
    () => new Map((data?.risks ?? []).map(risk => [risk.context.regionId, risk])), [data],
  );
  const selected = data?.regions.find(region => region.id === selection);
  const selectedRisk = selected ? riskByRegion.get(selected.id) : undefined;
  const selectedAlerts = data?.alerts.filter(alert => alert.regionId === selection) ?? [];
  const latest = useMemo(() => new Map((data?.readings ?? []).map(reading => [reading.sensorId, reading])), [data]);
  const selectedReadings = data?.sensors.flatMap(sensor => {
    const reading = latest.get(sensor.id);
    return sensor.regionId === selection && reading ? [{ sensor, reading }] : [];
  }) ?? [];
  const usableRisks = data?.risks.filter(risk => risk.context.readings > 0) ?? [];
  const generalRisk = isDemoMode ? dashboardMetrics.generalRisk
    : usableRisks.reduce<RiskLevel | null>((highest, risk) =>
      riskRank.indexOf(risk.context.riskLevel) > (highest ? riskRank.indexOf(highest) : -1)
        ? risk.context.riskLevel : highest, null);

  function refresh() {
    setLoad({ status: 'loading' });
    setReload(value => value + 1);
    setRecommendation(null);
  }

  function openRegion(id: number) {
    setSelection(id);
    setRecommendation(null);
    setScreen('details');
  }

  async function requestRecommendation(id: number) {
    const request: Load<Recommendation> = { status: 'loading' };
    setRecommendation(request);
    let result: Load<Recommendation>;
    try {
      result = { status: 'ready', data: await fetchRecommendation(id) };
    } catch (error) {
      result = { status: 'error', message: message(error) };
    }
    // A late result cannot overwrite a different region's recommendation.
    setRecommendation(current => current === request ? result : current);
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      {!entered ? (
        <View style={styles.loginWrap}>
          <Text style={styles.title}>Orbital Alert</Text>
          <Text style={styles.subtitle}>{isDemoMode
            ? 'Demonstração com dados simulados no aplicativo.'
            : 'Monitoramento preventivo de regiões com dados da plataforma local.'}</Text>
          <Action label={isDemoMode ? 'Abrir demonstração' : 'Abrir painel'} onPress={() => setScreen('dashboard')} />
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.topBar}>
            <Text style={styles.logo}>🌍 Orbital Alert</Text>
            <View style={styles.menuRow}>
              <TouchableOpacity accessibilityRole="button" onPress={() => setScreen('dashboard')}><Text style={styles.menu}>Dashboard</Text></TouchableOpacity>
              <TouchableOpacity accessibilityRole="button" onPress={() => setScreen('regions')}><Text style={styles.menu}>Regiões</Text></TouchableOpacity>
            </View>
          </View>
          <Text style={styles.sourceLine}>{isDemoMode
            ? 'Fonte: demonstração • dados simulados no aplicativo'
            : 'Fonte: API Orbital Alert • sensores da demonstração são simulados'}</Text>
          {!isDemoMode && <Action label="Atualizar dados" onPress={refresh} />}
          {!data && load.status === 'loading' && <Text style={styles.sectionText}>Carregando dados da API…</Text>}
          {!data && load.status === 'error' && (
            <View style={styles.alertCard} accessibilityRole="alert">
              <Text style={styles.alertTitle}>Falha de integração</Text>
              <Text style={styles.alertLine}>{load.message}</Text>
            </View>
          )}

          {data && screen === 'dashboard' && (
            <>
              <Text style={styles.sectionTitle}>Visão geral</Text>
              <View style={styles.metricsRow}>
                <MetricCard title="Alertas ativos" value={String(data.alerts.length)} highlight={colors.critical} />
                <MetricCard title="Regiões" value={String(data.regions.length)} highlight={colors.primary} />
              </View>
              <View style={styles.metricsRow}>
                <MetricCard title="Sensores ativos" value={String(isDemoMode
                  ? dashboardMetrics.onlineSensors : data.sensors.filter(sensor => sensor.status === 'ACTIVE').length)} highlight={colors.accent} />
                <MetricCard title="Maior nível de risco" value={generalRisk ? riskLabel[generalRisk] : 'Sem dados'} highlight={generalRisk ? riskColors[generalRisk] : colors.textMuted} />
              </View>
              {data.regions.length === 0 && <Text style={styles.sectionText}>Nenhuma região cadastrada.</Text>}
              {data.alerts.length === 0 && <Text style={styles.sectionText}>Nenhum alerta ativo.</Text>}
              {usableRisks.map(({ dataSource, context }) => {
                const region = data.regions.find(item => item.id === context.regionId);
                if (!region) return null;
                return (
                  <TouchableOpacity key={context.regionId} accessibilityRole="button" style={styles.regionCard} onPress={() => openRegion(region.id)}>
                    <Text style={styles.regionName}>{region.name}</Text>
                    <Text style={styles.regionMeta}>Risk Score IoT: {context.riskScore}/100 · {riskLabel[context.riskLevel]}</Text>
                    <Text style={styles.score}>{riskSource[dataSource]} · {utc(context.generatedAt)}</Text>
                  </TouchableOpacity>
                );
              })}
            </>
          )}

          {data && screen === 'regions' && (
            <>
              <Text style={styles.sectionTitle}>Regiões monitoradas</Text>
              {data.regions.length === 0 && <Text style={styles.sectionText}>Nenhuma região cadastrada.</Text>}
              {data.regions.map(region => {
                const risk = riskByRegion.get(region.id);
                return (
                  <TouchableOpacity key={region.id} accessibilityRole="button" style={styles.regionCard} onPress={() => openRegion(region.id)}>
                    <Text style={styles.regionName}>{region.name}</Text>
                    <Text style={styles.regionMeta}>{region.city}/{region.state} · Sensores cadastrados: {region.sensorsCount}</Text>
                    <Text style={styles.score}>{isDemoMode ? `Score satélite simulado: ${region.satelliteRiskScore}`
                      : risk && risk.context.readings > 0 ? `Risk Score IoT: ${risk.context.riskScore}/100 · ${riskSource[risk.dataSource]}` : 'Risk Score IoT indisponível'}</Text>
                  </TouchableOpacity>
                );
              })}
            </>
          )}

          {data && screen === 'details' && (
            <View style={styles.alertCard}>
              <Text style={styles.sectionTitle}>{selected?.name ?? 'Região indisponível'}</Text>
              {selected && (
                <>
                  <Text style={styles.alertLine}>{selected.city}/{selected.state}</Text>
                  {selectedAlerts.length === 0 && <Text style={styles.alertLine}>Nenhum alerta ativo nesta região.</Text>}
                  {selectedAlerts.map(alert => (
                    <View key={alert.id}>
                      <Text style={styles.alertTitle}>{alert.title} · {riskLabel[alert.severity]}</Text>
                      <Text style={styles.alertLine}>{alert.reason}</Text>
                      {alert.createdAt && <Text style={styles.alertLine}>Alerta #{alert.id} · {utc(alert.createdAt)}</Text>}
                      {alert.sensorData && <Text style={styles.alertLine}>{alert.sensorData}</Text>}
                      {alert.recommendedAction && <Text style={styles.alertLine}>Sugestão simulada: {alert.recommendedAction}</Text>}
                    </View>
                  ))}
                  {isDemoMode ? <Text style={styles.alertLine}>Score satélite simulado: {selected.satelliteRiskScore}</Text> : (
                    <>
                      <Text style={styles.alertTitle}>Últimas leituras</Text>
                      {selectedReadings.length === 0 && <Text style={styles.alertLine}>Nenhuma leitura registrada nesta região.</Text>}
                      {selectedReadings.map(({ sensor, reading }) => (
                        <Text key={sensor.id} style={styles.alertLine}>{sensor.type}: {reading.value} {sensor.unit} · leitura #{reading.id} · {utc(reading.measuredAt)}</Text>
                      ))}
                      <Text style={styles.alertTitle}>Indicadores de risco</Text>
                      {selectedRisk && selectedRisk.context.readings > 0 ? (
                        <>
                          <Text style={styles.alertLine}>Risk Score IoT: {selectedRisk.context.riskScore}/100 · {riskSource[selectedRisk.dataSource]} · {utc(selectedRisk.context.generatedAt)}</Text>
                          {selectedRisk.context.indicators.map(indicator => (
                            <Text key={indicator.sensorType} style={styles.alertLine}>{indicator.sensorType}: média {indicator.avgValue} {indicator.unit} · contribuição {indicator.subScore}/100</Text>
                          ))}
                        </>
                      ) : <Text style={styles.alertLine}>Sem indicadores de risco para esta região.</Text>}
                      {recommendation?.status !== 'loading' && <Action label="Consultar recomendação" onPress={() => requestRecommendation(selected.id)} />}
                      {recommendation?.status === 'loading' && <Text style={styles.alertLine}>Consultando recomendação…</Text>}
                      {recommendation?.status === 'error' && <Text accessibilityRole="alert" style={styles.alertLine}>Recomendação indisponível. {recommendation.message}</Text>}
                      {recommendation?.status === 'ready' && (
                        <>
                          <Text style={styles.alertTitle}>Recomendação consultiva</Text>
                          <Text style={styles.alertLine}>{recommendation.data.aiMode} · {riskSource[recommendation.data.dataSource]} · {utc(recommendation.data.generatedAt)}</Text>
                          <Text style={styles.alertLine}>{recommendation.data.recommendation}</Text>
                        </>
                      )}
                    </>
                  )}
                </>
              )}
              <Action label="Voltar para regiões" onPress={() => setScreen('regions')} />
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}


const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  loginWrap: { flex: 1, justifyContent: 'center', alignSelf: 'center', width: '100%', maxWidth: 620, padding: 24, gap: 12 },
  content: { alignSelf: 'center', width: '100%', maxWidth: 820, padding: 18, paddingBottom: 28 },
  title: { color: colors.text, fontSize: 34, fontWeight: '800' },
  subtitle: { color: colors.textMuted, fontSize: 15, marginBottom: 10, lineHeight: 21 },
  button: { backgroundColor: colors.primary, borderRadius: 12, alignItems: 'center', paddingVertical: 13, paddingHorizontal: 16, marginBottom: 14 },
  buttonText: { color: '#04122B', fontWeight: '700' },
  topBar: { marginBottom: 14, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  logo: { color: colors.text, fontWeight: '700', fontSize: 18 },
  menuRow: { flexDirection: 'row', gap: 12 },
  menu: { color: colors.textMuted, fontSize: 13 },
  sectionTitle: { color: colors.text, fontSize: 22, fontWeight: '700', marginBottom: 8 },
  sectionText: { color: colors.textMuted, marginBottom: 14, lineHeight: 20 },
  sourceLine: { color: colors.textMuted, fontSize: 12, marginBottom: 12 },
  metricsRow: { flexDirection: 'row', gap: 10 },
  regionCard: { backgroundColor: colors.cardSoft, borderRadius: 14, borderWidth: 1, borderColor: colors.border, padding: 14, marginBottom: 10 },
  regionName: { color: colors.text, fontWeight: '700', fontSize: 16, marginBottom: 6 },
  regionMeta: { color: colors.textMuted, marginBottom: 8 },
  score: { color: colors.textMuted },
  alertCard: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 14, padding: 16 },
  alertTitle: { color: colors.text, fontSize: 18, fontWeight: '700', marginBottom: 10 },
  alertLine: { color: colors.textMuted, marginBottom: 8, lineHeight: 20 }
});
