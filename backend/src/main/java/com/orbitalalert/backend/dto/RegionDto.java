package com.orbitalalert.backend.dto;
import com.orbitalalert.backend.entity.RiskLevel;import jakarta.validation.constraints.*;
public record RegionDto(Long id,@NotBlank String name,@NotBlank String city,@NotBlank @Size(min=2,max=2) String state,@NotNull Double latitude,@NotNull Double longitude,@NotNull @DecimalMin("0.0") @DecimalMax("100.0") Double satelliteRiskScore,@NotNull RiskLevel riskLevel) {}
