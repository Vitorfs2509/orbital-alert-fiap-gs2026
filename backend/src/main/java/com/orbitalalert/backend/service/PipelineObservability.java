package com.orbitalalert.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.orbitalalert.backend.entity.AlertStatus;
import com.orbitalalert.backend.repository.AlertRepository;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;

@Service
public class PipelineObservability {
    private static final Logger LOG = LoggerFactory.getLogger(PipelineObservability.class);
    private final Counter received;
    private final Counter processed;
    private final Counter failures;
    private final Counter rawFailures;
    private final Counter generatedAlerts;
    private final AlertRepository alerts;
    private final DataLakeService dataLake;
    private final ObjectMapper json;

    public PipelineObservability(MeterRegistry meters, AlertRepository alerts, DataLakeService dataLake,
                                 ObjectMapper json) {
        this.received = meters.counter("orbital.readings.received");
        this.processed = meters.counter("orbital.readings.processed");
        this.failures = meters.counter("orbital.readings.failures");
        this.rawFailures = meters.counter("orbital.raw.failures");
        this.generatedAlerts = meters.counter("orbital.alerts.generated");
        this.alerts = alerts;
        this.dataLake = dataLake;
        this.json = json;
        meters.gauge("orbital.alerts.active", this, value -> value.countActive());
    }

    public void received() { received.increment(); }

    public void processed(long readingId, long sensorId, boolean alertGenerated, boolean rawStored) {
        processed.increment();
        if (alertGenerated) generatedAlerts.increment();
        if (!rawStored && dataLake.isEnabled()) rawFailures.increment();
        LOG.atInfo().addKeyValue("reading_id", readingId).addKeyValue("sensor_id", sensorId)
                .addKeyValue("alert_generated", alertGenerated).addKeyValue("raw_stored", rawStored)
                .log("reading_processed");
    }

    public void failed(long sensorId, RuntimeException error) {
        failures.increment();
        LOG.atWarn().addKeyValue("sensor_id", sensorId).addKeyValue("reason", error.getClass().getSimpleName())
                .log("reading_failed");
    }

    private long countActive() {
        return alerts.countByStatusIn(List.of(AlertStatus.OPEN, AlertStatus.MONITORING));
    }

    private JsonNode etlStatus() {
        var path = dataLake.getBasePath().resolve("control/etl-status.json");
        try {
            if (Files.isRegularFile(path)) return json.readTree(path.toFile());
            return json.createObjectNode().put("status", "NEVER_RUN");
        } catch (IOException error) {
            return json.createObjectNode().put("status", "UNREADABLE");
        }
    }

    public Map<String, Object> status() {
        return Map.of("api", "UP", "readingsReceived", received.count(), "readingsProcessed", processed.count(),
                "readingFailures", failures.count(), "rawFailures", rawFailures.count(),
                "alertsGenerated", generatedAlerts.count(), "alertsActive", countActive(), "etl", etlStatus());
    }
}
