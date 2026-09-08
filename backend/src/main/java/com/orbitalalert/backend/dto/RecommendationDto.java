package com.orbitalalert.backend.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Contratos da camada CURATED (Gold) e da recomendacao de IA generativa.
 *
 * <p>{@link RegionIndicator} e {@link RegionRisk} espelham exatamente o JSON
 * produzido por {@code etl/trusted_to_curated.py} em
 * {@code data-lake/curated/region_risk_latest.json}.
 */
public class RecommendationDto {

    /** Indicador agregado de um tipo de sensor dentro de uma regiao. */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record RegionIndicator(
            String sensorType,
            String unit,
            Integer samples,
            Double avgValue,
            Double minValue,
            Double maxValue,
            Double lastValue,
            Double baseline,
            Double threshold,
            String direction,
            String riskType,
            Integer subScore,
            String trend) {
    }

    /** Visao consolidada de risco de uma regiao (registro da camada CURATED). */
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record RegionRisk(
            Long regionId,
            String regionName,
            Integer riskScore,
            String riskLevel,
            String riskType,
            String dominantSensorType,
            Integer readings,
            Integer sensors,
            String windowStart,
            String windowEnd,
            List<RegionIndicator> indicators,
            List<String> ignoredSensorTypes,
            String generatedAt) {
    }

    /**
     * Resposta de {@code GET /api/recommendations/regions/{regionId}}.
     *
     * @param aiMode     MOCK ou o provedor externo efetivamente utilizado
     * @param dataSource CURATED_LAYER quando o Data Lake alimentou a IA,
     *                   OPERATIONAL_DB_FALLBACK quando a camada CURATED nao existia
     * @param context    o mesmo contexto enviado ao modelo, exposto para auditoria
     */
    public record RecommendationResponse(
            Long regionId,
            String regionName,
            Integer riskScore,
            String riskLevel,
            String riskType,
            String recommendation,
            LocalDateTime generatedAt,
            String aiMode,
            String dataSource,
            RegionRisk context) {
    }

    /** Prompt exibido por {@code GET /api/recommendations/regions/{id}/prompt}. */
    public record PromptResponse(Long regionId, String dataSource, String aiMode, String prompt) {
    }
}
