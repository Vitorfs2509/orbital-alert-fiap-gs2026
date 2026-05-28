package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.AlertDto;
import com.orbitalalert.backend.entity.Alert;
import com.orbitalalert.backend.entity.AlertStatus;
import com.orbitalalert.backend.entity.RiskLevel;
import com.orbitalalert.backend.entity.Sensor;
import com.orbitalalert.backend.entity.SensorType;
import com.orbitalalert.backend.exception.NotFoundException;
import com.orbitalalert.backend.repository.AlertRepository;
import java.time.LocalDateTime;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class AlertService {
    private final AlertRepository alertRepository;

    public AlertService(AlertRepository alertRepository) {
        this.alertRepository = alertRepository;
    }

    public List<AlertDto> list() {
        return alertRepository.findAll().stream().map(this::map).toList();
    }

    public List<AlertDto> active() {
        return alertRepository.findAll().stream()
                .filter(alert -> alert.getStatus() == AlertStatus.ACTIVE)
                .map(this::map)
                .toList();
    }

    public AlertDto resolve(Long id) {
        Alert alert = alertRepository.findById(id)
                .orElseThrow(() -> new NotFoundException("Alerta não encontrado"));
        alert.setStatus(AlertStatus.RESOLVED);
        alert.setResolvedAt(LocalDateTime.now());
        return map(alertRepository.save(alert));
    }

    public void createFromReading(Sensor sensor, Double value) {
        Alert alert = null;

        if (sensor.getType() == SensorType.WATER_LEVEL && value >= 80) {
            alert = buildAlert(sensor, "Risco de enchente", "Nível de água acima do limite seguro.", RiskLevel.HIGH);
        }

        if (sensor.getType() == SensorType.TEMPERATURE && value >= 40) {
            alert = buildAlert(sensor, "Temperatura elevada", "Temperatura alta indica risco de queimada.", RiskLevel.HIGH);
        }

        if (sensor.getType() == SensorType.SMOKE && value >= 70) {
            alert = buildAlert(sensor, "Alerta de fumaça/incêndio", "Índice de fumaça acima do limite seguro.", RiskLevel.CRITICAL);
        }

        if (sensor.getType() == SensorType.RAINFALL && value >= 60) {
            alert = buildAlert(sensor, "Chuva intensa", "Volume de chuva elevado na região monitorada.", RiskLevel.HIGH);
        }

        if (alert != null) {
            alertRepository.save(alert);
        }
    }

    private AlertDto map(Alert alert) {
        return new AlertDto(
                alert.getId(),
                alert.getRegion().getId(),
                alert.getRegion().getName(),
                alert.getTitle(),
                alert.getDescription(),
                alert.getSeverity(),
                alert.getStatus(),
                alert.getCreatedAt(),
                alert.getResolvedAt()
        );
    }

    private Alert buildAlert(Sensor sensor, String title, String description, RiskLevel severity) {
        Alert alert = new Alert();
        alert.setRegion(sensor.getRegion());
        alert.setTitle(title);
        alert.setDescription(description);
        alert.setSeverity(severity);
        alert.setStatus(AlertStatus.ACTIVE);
        return alert;
    }
}
