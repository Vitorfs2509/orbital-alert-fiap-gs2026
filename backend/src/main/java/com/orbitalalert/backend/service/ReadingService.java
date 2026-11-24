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

    public ReadingService(SensorReadingRepository repo, SensorRepository sensors, AlertService alerts,
                          DataLakeService dataLake, PipelineObservability metrics) {
        this.repo = repo;
        this.sensors = sensors;
        this.alerts = alerts;
        this.dataLake = dataLake;
        this.metrics = metrics;
    }

    public ReadingResponse create(CreateReadingRequest request) {
        long sensorId = request.sensorId();
        metrics.received();
        try {
            var sensor = sensors.findById(sensorId)
                    .orElseThrow(() -> new NotFoundException("Sensor não encontrado"));
            var now = LocalDateTime.now(ZoneOffset.UTC);
            var reading = new SensorReading();
            reading.setSensor(sensor);
            reading.setValue(request.value());
            reading.setMeasuredAt(now);
            reading = repo.save(reading);
            var alert = alerts.createFromReading(sensor, request.value());
            String source = request.source() == null || request.source().isBlank() ? "API" : request.source();
            boolean rawStored = dataLake.writeRawEvent(new RawEventDto(UUID.randomUUID().toString(),
                    sensorId, sensor.getRegion().getId(), sensor.getType().name(), request.value(), sensor.getUnit(),
                    now, now, source, reading.getId()));
            metrics.processed(reading.getId(), sensorId, alert != null, rawStored);
            return map(reading);
        } catch (RuntimeException error) {
            metrics.failed(sensorId, error);
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
