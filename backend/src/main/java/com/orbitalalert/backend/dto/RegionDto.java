package com.orbitalalert.backend.dto;

import com.orbitalalert.backend.entity.RiskLevel;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record RegionDto(
        Long id,
        @NotBlank String name,
        @NotBlank String city,
        @NotBlank @Size(min = 2, max = 2) String state,
        @NotNull @DecimalMin("-90.0") @DecimalMax("90.0") Double latitude,
        @NotNull @DecimalMin("-180.0") @DecimalMax("180.0") Double longitude,
        @NotNull @DecimalMin("0.0") @DecimalMax("100.0") Double satelliteRiskScore,
        @NotNull RiskLevel riskLevel
) {
}
