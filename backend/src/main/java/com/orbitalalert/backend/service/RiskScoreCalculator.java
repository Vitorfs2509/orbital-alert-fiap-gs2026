package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RecommendationDto.RegionIndicator;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import com.orbitalalert.backend.entity.Region;
import com.orbitalalert.backend.entity.SensorReading;
import com.orbitalalert.backend.entity.SensorType;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Calculo de risco por regiao a partir do banco operacional.
 *
 * <p>Usado apenas como fallback do {@link RecommendationService} quando a
 * camada CURATED do Data Lake ainda nao foi gerada. As regras replicam
 * exatamente {@code etl/trusted_to_curated.py}, para que o mesmo cenario
 * produza o mesmo score nos dois caminhos.
 *
 * <p>O modelo e deterministico e sem machine learning:
 * <pre>
 *   subScore    = 100 * (media - baseline) / (limiar - baseline), cortado em 0..100
 *   scoreRegiao = 0.7 * maior(subScore) + 0.3 * media(subScore) + 10 se em alta
 *   nivel       = HIGH (>= 70) | MEDIUM (>= 40) | LOW
 * </pre>
 */
@Component
public class RiskScoreCalculator {

    /** baseline = valor normal (0 pontos); limit = limiar de alerta (100 pontos). */
    private record Rule(double baseline, double limit, String direction, String riskType) {
    }

    private static final Map<SensorType, Rule> RULES = Map.of(
            SensorType.WATER_LEVEL, new Rule(20.0, 80.0, "above", "FLOOD"),
            SensorType.RAINFALL, new Rule(0.0, 60.0, "above", "FLOOD"),
            SensorType.TEMPERATURE, new Rule(25.0, 40.0, "above", "FIRE"),
            SensorType.SMOKE, new Rule(10.0, 70.0, "above", "FIRE"),
            SensorType.HUMIDITY, new Rule(60.0, 30.0, "below", "FIRE"));

    private static final int LEVEL_HIGH = 70;
    private static final int LEVEL_MEDIUM = 40;
    private static final double WEIGHT_MAX = 0.7;
    private static final double WEIGHT_MEAN = 0.3;
    private static final int TREND_BONUS = 10;

    public RegionRisk fromReadings(Region region, List<SensorReading> readings) {
        String generatedAt = LocalDateTime.now().toString();

        if (readings == null || readings.isEmpty()) {
            return new RegionRisk(region.getId(), region.getName(), 0, "LOW", "NONE", null,
                    0, 0, null, null, List.of(), List.of(), generatedAt);
        }

        List<SensorReading> ordered = new ArrayList<>(readings);
        ordered.sort(Comparator.comparing(SensorReading::getMeasuredAt));

        Map<SensorType, List<SensorReading>> byType = new LinkedHashMap<>();
        List<String> ignoredTypes = new ArrayList<>();
        for (SensorReading reading : ordered) {
            SensorType type = reading.getSensor().getType();
            if (RULES.containsKey(type)) {
                byType.computeIfAbsent(type, key -> new ArrayList<>()).add(reading);
            } else if (!ignoredTypes.contains(type.name())) {
                ignoredTypes.add(type.name());
            }
        }

        List<RegionIndicator> indicators = new ArrayList<>();
        byType.forEach((type, typeReadings) -> indicators.add(buildIndicator(type, typeReadings)));
        indicators.sort(Comparator.comparing(RegionIndicator::subScore).reversed());

        int sensors = (int) ordered.stream().map(r -> r.getSensor().getId()).distinct().count();
        String windowStart = ordered.get(0).getMeasuredAt().toString();
        String windowEnd = ordered.get(ordered.size() - 1).getMeasuredAt().toString();

        if (indicators.isEmpty()) {
            return new RegionRisk(region.getId(), region.getName(), 0, "LOW", "NONE", null,
                    ordered.size(), sensors, windowStart, windowEnd, List.of(), ignoredTypes, generatedAt);
        }

        RegionIndicator dominant = indicators.get(0);
        double maxSub = dominant.subScore();
        double meanSub = indicators.stream().mapToInt(RegionIndicator::subScore).average().orElse(0.0);
        int bonus = "RISING".equals(dominant.trend()) ? TREND_BONUS : 0;
        int score = (int) clamp(Math.round(WEIGHT_MAX * maxSub + WEIGHT_MEAN * meanSub) + bonus, 0, 100);

        String level = score >= LEVEL_HIGH ? "HIGH" : score >= LEVEL_MEDIUM ? "MEDIUM" : "LOW";
        String riskType = "LOW".equals(level) ? "NONE" : dominant.riskType();

        return new RegionRisk(region.getId(), region.getName(), score, level, riskType,
                dominant.sensorType(), ordered.size(), sensors, windowStart, windowEnd,
                indicators, ignoredTypes, generatedAt);
    }

    private RegionIndicator buildIndicator(SensorType type, List<SensorReading> readings) {
        Rule rule = RULES.get(type);
        List<Double> values = readings.stream().map(SensorReading::getValue).toList();

        double average = values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        double min = values.stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
        double max = values.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
        double last = values.get(values.size() - 1);

        String trend = computeTrend(values);
        // Umidade e um risco invertido: cair e o que aumenta o risco.
        if ("below".equals(rule.direction())) {
            trend = "RISING".equals(trend) ? "FALLING" : "FALLING".equals(trend) ? "RISING" : trend;
        }

        return new RegionIndicator(type.name(), readings.get(0).getSensor().getUnit(), values.size(),
                round2(average), round2(min), round2(max), round2(last),
                rule.baseline(), rule.limit(), rule.direction(), rule.riskType(),
                subScore(rule, average), trend);
    }

    private int subScore(Rule rule, double average) {
        double span = rule.limit() - rule.baseline();
        if (span == 0.0) {
            return 0;
        }
        double ratio = (average - rule.baseline()) / span;
        return (int) clamp(Math.round(ratio * 100), 0, 100);
    }

    /** Compara a media da segunda metade da serie com a da primeira metade. */
    private String computeTrend(List<Double> values) {
        if (values.size() < 2) {
            return "INSUFFICIENT_DATA";
        }
        int half = values.size() / 2;
        double first = values.subList(0, half).stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        double second = values.subList(half, values.size()).stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        if (first == 0.0) {
            return second > 0.0 ? "RISING" : "STABLE";
        }
        double change = (second - first) / Math.abs(first);
        if (change > 0.05) {
            return "RISING";
        }
        if (change < -0.05) {
            return "FALLING";
        }
        return "STABLE";
    }

    private static double clamp(double value, double low, double high) {
        return Math.max(low, Math.min(high, value));
    }

    private static double round2(double value) {
        return Math.round(value * 100.0) / 100.0;
    }
}
