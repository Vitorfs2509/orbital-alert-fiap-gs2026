package com.orbitalalert.backend.entity;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter(autoApply = false)
public class AlertStatusConverter implements AttributeConverter<AlertStatus, String> {
    @Override
    public String convertToDatabaseColumn(AlertStatus status) {
        if (status == null) {
            return null;
        }
        return status == AlertStatus.RESOLVED ? "RESOLVED" : "OPEN";
    }

    @Override
    public AlertStatus convertToEntityAttribute(String value) {
        if (value == null) {
            return null;
        }
        return "RESOLVED".equals(value) ? AlertStatus.RESOLVED : AlertStatus.ACTIVE;
    }
}
