package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RawEventDto;
import com.orbitalalert.backend.dto.ReadingDto.CreateReadingRequest;
import com.orbitalalert.backend.dto.ReadingDto.ReadingResponse;
import com.orbitalalert.backend.entity.SensorReading;
import com.orbitalalert.backend.exception.NotFoundException;
import com.orbitalalert.backend.repository.SensorReadingRepository;
import com.orbitalalert.backend.repository.SensorRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;

@Service
public class ReadingService {
    private final SensorReadingRepository repo;
    private final SensorRepository sensors;
    private final AlertService alerts;
    private final DataLakeService dataLake;
    private final PipelineObservability metrics;
    private final ProcessEventLog events;

    public ReadingService(SensorReadingRepository repo, SensorRepository sensors, AlertService alerts,
                          DataLakeService dataLake, PipelineObservability metrics, ProcessEventLog events) {
        this.repo = repo;
        this.sensors = sensors;
        this.alerts = alerts;
        this.dataLake = dataLake;
        this.metrics = metrics;
        this.events = events;
    }

    public ReadingResponse create(CreateReadingRequest request) {
        long sensorId = request.sensorId();
        String source = request.source() == null || request.source().isBlank() ? "API" : request.source();
        var trace = new ProcessEventLog.Trace(UUID.randomUUID().toString(), sensorId, source);
        Long regionId = null;
        Long readingId = null;
        Long alertId = null;
        metrics.received();
        events.append(trace, "READING_RECEIVED", "SUCCESS", null, null, null);
        try {
            var sensor = sensors.findById(sensorId)
                    .orElseThrow(() -> new NotFoundException("Sensor não encontrado"));
            regionId = sensor.getRegion().getId();
            var now = LocalDateTime.now(ZoneOffset.UTC);
            var reading = new SensorReading();
            reading.setSensor(sensor);
            reading.setValue(request.value());
            reading.setMeasuredAt(now);
            reading = repo.save(reading);
            readingId = reading.getId();
            events.append(trace, "READING_PERSISTED", "SUCCESS", regionId, readingId, null);
            var alert = alerts.createFromReading(sensor, request.value());
            alertId = alert == null ? null : alert.getId();
            events.append(trace, "RISK_EVALUATED", "SUCCESS", regionId, readingId, alertId);
            if (alertId != null) events.append(trace, "ALERT_GENERATED", "SUCCESS", regionId, readingId, alertId);
            boolean rawStored = dataLake.writeRawEvent(new RawEventDto(UUID.randomUUID().toString(),
                    sensorId, regionId, sensor.getType().name(), request.value(), sensor.getUnit(),
                    now, now, source, readingId, trace.caseId()));
            events.append(trace, rawStored ? "RAW_STORED" : "RAW_NOT_STORED",
                    rawStored ? "SUCCESS" : dataLake.isEnabled() ? "FAILED" : "DISABLED",
                    regionId, readingId, alertId);
            metrics.processed(reading.getId(), sensorId, alert != null, rawStored);
            return map(reading);
        } catch (RuntimeException error) {
            metrics.failed(sensorId, error);
            events.append(trace, error instanceof NotFoundException ? "READING_REJECTED" : "READING_FAILED",
                    "FAILED", regionId, readingId, alertId);
            throw error;
        }
    }

    public List<ReadingResponse> latest() {
        return repo.findLatestPerSensor().stream().map(this::map).toList();
    }

    private ReadingResponse map(SensorReading reading) {
        return new ReadingResponse(reading.getId(), reading.getSensor().getId(),
                reading.getSensor().getType().name(), reading.getValue(), reading.getMeasuredAt());
    }
}
