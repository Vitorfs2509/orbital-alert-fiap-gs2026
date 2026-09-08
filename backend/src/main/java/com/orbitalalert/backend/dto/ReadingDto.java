package com.orbitalalert.backend.dto;
import jakarta.validation.constraints.*;import java.time.LocalDateTime;
public class ReadingDto {
 // `source` e opcional: identifica a origem do evento na camada RAW do Data Lake.
 public record CreateReadingRequest(@NotNull Long sensorId, @NotNull Double value, String source){}
 public record ReadingResponse(Long id, Long sensorId, String sensorType, Double value, LocalDateTime measuredAt){}
}
