package com.orbitalalert.backend.dto;
import jakarta.validation.constraints.*;import java.time.LocalDateTime;
public class ReadingDto {
 public record CreateReadingRequest(@NotNull Long sensorId, @NotNull Double value){}
 public record ReadingResponse(Long id, Long sensorId, String sensorType, Double value, LocalDateTime measuredAt){}
}
