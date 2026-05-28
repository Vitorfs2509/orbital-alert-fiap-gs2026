package com.orbitalalert.backend.dto;
import com.orbitalalert.backend.entity.SensorStatus;import com.orbitalalert.backend.entity.SensorType;import jakarta.validation.constraints.*;
public record SensorDto(Long id,@NotNull Long regionId,@NotNull SensorType type,@NotNull SensorStatus status,@NotBlank String unit) {}
