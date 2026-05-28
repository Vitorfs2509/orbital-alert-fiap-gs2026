package com.orbitalalert.backend.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;
import java.time.LocalDateTime;

public class ReadingDto {
    public record CreateReadingRequest(
            @NotNull @Positive Long sensorId,
            @NotNull @PositiveOrZero Double value
    ) {
    }

    public record ReadingResponse(
            Long id,
            Long sensorId,
            String sensorType,
            Double value,
            LocalDateTime measuredAt
    ) {
    }
}
