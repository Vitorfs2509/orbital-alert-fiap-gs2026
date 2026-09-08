import React, { useEffect, useMemo, useState } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { alerts as mockAlerts, dashboardMetrics, regions } from './src/data/mockData';
import { MetricCard } from './src/components/MetricCard';
import { DataSource, fetchAlerts, isBackendConfigured } from './src/services/api';
import { Alert, Region, RiskLevel } from './src/types';
import { colors } from './src/theme/colors';

type Screen = 'login' | 'dashboard' | 'regions' | 'alert-details' | 'region-details';

const riskColor = (risk: RiskLevel) => ({ LOW: colors.low, MEDIUM: colors.medium, HIGH: colors.high, CRITICAL: colors.critical }[risk]);

export default function App() {
  const [screen, setScreen] = useState<Screen>('login');
  const [email, setEmail] = useState('demo@orbitalalert.app');
  const [password, setPassword] = useState('123456');
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(mockAlerts[0]);

  // Alertas: backend real quando EXPO_PUBLIC_API_BASE_URL existe, mock caso contrário.
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [dataSource, setDataSource] = useState<DataSource>('MOCK');

  useEffect(() => {
    if (!isBackendConfigured) return;

    let active = true;
    fetchAlerts()
      .then(remote => {
        // Sem alertas no backend, o mock continua valendo para a demonstração.
        if (!active || remote.length === 0) return;
        setAlerts(remote);
        setDataSource('BACKEND');
      })
      .catch(() => {
        // API fora do ar: segue com o mock, sem quebrar a interface.
      });

    return () => {
      active = false;
    };
  }, []);

  const activeAlerts = useMemo(() => alerts.filter(a => a.status !== 'RESOLVED').length, [alerts]);

  const regionById = useMemo(() => new Map(regions.map(r => [r.id, r])), []);

  const mockLogin = () => {
    if (email.trim() && password.trim()) setScreen('dashboard');
  };

  const openRegion = (region: Region) => {
    setSelectedRegion(region);

    const related = alerts.find(
      (alert) => alert.regionId === region.id && alert.status !== 'RESOLVED'
    );

    if (related) {
      setSelectedAlert(related);
      setScreen('alert-details');
      return;
    }

    setSelectedAlert(null);
    setScreen('region-details');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      {screen === 'login' && (
        <View style={styles.loginWrap}>
          <Text style={styles.title}>Orbital Alert</Text>
          <Text style={styles.subtitle}>Monitoramento preventivo com dados simulados de satélite + IoT.</Text>
          <TextInput style={styles.input} placeholder="E-mail" placeholderTextColor={colors.textMuted} value={email} onChangeText={setEmail} autoCapitalize="none" />
          <TextInput style={styles.input} placeholder="Senha" placeholderTextColor={colors.textMuted} value={password} onChangeText={setPassword} secureTextEntry />
          <TouchableOpacity style={styles.button} onPress={mockLogin}>
            <Text style={styles.buttonText}>Entrar (modo acadêmico)</Text>
          </TouchableOpacity>
        </View>
      )}

      {screen !== 'login' && (
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.topBar}>
            <Text style={styles.logo}>🌍 Orbital Alert</Text>
            <View style={styles.menuRow}>
              <TouchableOpacity onPress={() => setScreen('dashboard')}><Text style={styles.menu}>Dashboard</Text></TouchableOpacity>
              <TouchableOpacity onPress={() => setScreen('regions')}><Text style={styles.menu}>Regiões</Text></TouchableOpacity>
            </View>
          </View>

          {screen === 'dashboard' && (
            <>
              <Text style={styles.sectionTitle}>Visão Geral</Text>
              <Text style={styles.sectionText}>Dados de enchente e clima indicam risco em regiões monitoradas para apoiar ações preventivas.</Text>
              <Text style={styles.sourceLine}>
                {dataSource === 'BACKEND' ? '🟢 Alertas do backend real (GET /api/alerts)' : '⚪ Alertas em modo demonstração (dados mockados)'}
              </Text>
              <View style={styles.metricsRow}>
                <MetricCard title="Alertas ativos" value={String(activeAlerts)} highlight={colors.critical} />
                <MetricCard title="Regiões" value={String(dashboardMetrics.monitoredRegions)} highlight={colors.primary} />
              </View>
              <View style={styles.metricsRow}>
                <MetricCard title="Sensores online" value={String(dashboardMetrics.onlineSensors)} highlight={colors.accent} />
                <MetricCard title="Risco geral" value={dashboardMetrics.generalRisk} highlight={riskColor(dashboardMetrics.generalRisk)} />
              </View>
            </>
          )}

          {screen === 'regions' && (
            <>
              <Text style={styles.sectionTitle}>Regiões Monitoradas</Text>
              {regions.map(region => (
                <TouchableOpacity key={region.id} style={styles.regionCard} onPress={() => openRegion(region)}>
                  <Text style={styles.regionName}>{region.name}</Text>
                  <Text style={styles.regionMeta}>{region.city}/{region.state} • Sensores: {region.sensorsCount}</Text>
                  <View style={styles.badgeRow}>
                    <Text style={[styles.badge, { color: riskColor(region.riskLevel), borderColor: riskColor(region.riskLevel) }]}>{region.riskLevel}</Text>
                    <Text style={styles.score}>Score satélite: {region.satelliteRiskScore}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </>
          )}

          {screen === 'region-details' && selectedRegion && (
            <View style={styles.alertCard}>
              <Text style={styles.sectionTitle}>Detalhes de Monitoramento</Text>
              <Text style={styles.alertTitle}>{selectedRegion.name}</Text>
              <Text style={styles.alertLine}>Região: {selectedRegion.city}/{selectedRegion.state}</Text>
              <Text style={styles.alertLine}>Nível de risco: <Text style={{ color: riskColor(selectedRegion.riskLevel) }}>{selectedRegion.riskLevel}</Text></Text>
              <Text style={styles.alertLine}>Score satélite: {selectedRegion.satelliteRiskScore}</Text>
              <Text style={styles.alertLine}>Sensores ativos: {selectedRegion.sensorsCount}</Text>
              <Text style={styles.alertLine}>Status: MONITORING</Text>
              <Text style={styles.alertLine}>Ação recomendada: manter acompanhamento preventivo da região e validar leituras dos sensores IoT.</Text>
              <Text style={styles.alertLine}>Explicação: esta região não possui alerta ativo no momento, mas continua sendo monitorada por dados simulados de satélite e sensores IoT.</Text>
              <TouchableOpacity style={[styles.button, { marginTop: 14 }]} onPress={() => setScreen('regions')}>
                <Text style={styles.buttonText}>Voltar para Regiões</Text>
              </TouchableOpacity>
            </View>
          )}

          {screen === 'alert-details' && selectedAlert && (
            <View style={styles.alertCard}>
              <Text style={styles.sectionTitle}>Detalhes do Alerta</Text>
              <Text style={styles.alertTitle}>{selectedAlert.title}</Text>
              <Text style={styles.alertLine}>Região: {regionById.get(selectedAlert.regionId)?.name ?? 'N/A'}</Text>
              <Text style={styles.alertLine}>Severidade: <Text style={{ color: riskColor(selectedAlert.severity) }}>{selectedAlert.severity}</Text></Text>
              <Text style={styles.alertLine}>Status: {selectedAlert.status}</Text>
              <Text style={styles.alertLine}>Dados do sensor: {selectedAlert.sensorData}</Text>
              <Text style={styles.alertLine}>Por que foi gerado: {selectedAlert.reason}</Text>
              <Text style={styles.alertLine}>Ação recomendada: {selectedAlert.recommendedAction}</Text>
              <TouchableOpacity style={[styles.button, { marginTop: 14 }]} onPress={() => setScreen('regions')}>
                <Text style={styles.buttonText}>Voltar para Regiões</Text>
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  loginWrap: { flex: 1, justifyContent: 'center', padding: 24, gap: 12 },
  content: { padding: 18, paddingBottom: 28 },
  title: { color: colors.text, fontSize: 34, fontWeight: '800' },
  subtitle: { color: colors.textMuted, fontSize: 15, marginBottom: 10, lineHeight: 21 },
  input: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, color: colors.text, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12 },
  button: { backgroundColor: colors.primary, borderRadius: 12, alignItems: 'center', paddingVertical: 13, marginTop: 6 },
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
  badgeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  badge: { borderWidth: 1, paddingHorizontal: 10, paddingVertical: 3, borderRadius: 999, fontWeight: '700', overflow: 'hidden' },
  score: { color: colors.textMuted },
  alertCard: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 14, padding: 16 },
  alertTitle: { color: colors.text, fontSize: 18, fontWeight: '700', marginBottom: 10 },
  alertLine: { color: colors.textMuted, marginBottom: 8, lineHeight: 20 }
});
