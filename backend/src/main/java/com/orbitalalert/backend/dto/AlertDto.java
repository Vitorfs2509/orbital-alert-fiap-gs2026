package com.orbitalalert.backend.dto;
import com.orbitalalert.backend.entity.AlertStatus;import com.orbitalalert.backend.entity.RiskLevel;import java.time.LocalDateTime;
public record AlertDto(Long id,Long regionId,String regionName,String title,String description,RiskLevel severity,AlertStatus status,LocalDateTime createdAt,LocalDateTime resolvedAt) {}
