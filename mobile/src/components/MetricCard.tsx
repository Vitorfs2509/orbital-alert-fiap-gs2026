import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors } from '../theme/colors';

type Props = { title: string; value: string; highlight?: string };

export function MetricCard({ title, value, highlight = colors.primary }: Props) {
  return (
    <View style={[styles.card, { borderColor: highlight }]}> 
      <Text style={styles.title}>{title}</Text>
      <Text style={[styles.value, { color: highlight }]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: colors.card,
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10
  },
  title: { color: colors.textMuted, fontSize: 13, marginBottom: 8 },
  value: { color: colors.text, fontSize: 22, fontWeight: '700' }
});
