package com.orbitalalert.backend.dto;

import java.time.LocalDateTime;

/**
 * Evento bruto gravado na camada RAW (Bronze) do Data Lake.
 *
 * <p>Representa a leitura enriquecida pela API, identificada pelo ID operacional.
 * E gravado durante a ingestao e nunca substitui o banco. O consumo e feito pelo ETL
 * {@code etl/raw_to_trusted.py}.
 */
public record RawEventDto(
        String eventId,
        Long sensorId,
        Long regionId,
        String sensorType,
        Double value,
        String unit,
        LocalDateTime measuredAt,
        LocalDateTime receivedAt,
        String source,
        Long readingId) {
}
