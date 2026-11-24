package com.orbitalalert.backend.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.UUID;

@Service
public class ProcessEventLog {
    private static final Logger LOG = LoggerFactory.getLogger(ProcessEventLog.class);

    public record Trace(String caseId, long sensorId, String source) {}

    private final DataLakeService lake;
    private final ObjectMapper json;

    public ProcessEventLog(DataLakeService lake, ObjectMapper json) {
        this.lake = lake;
        this.json = json;
    }

    public synchronized void append(Trace trace, String activity, String status,
                                    Long regionId, Long readingId, Long alertId) {
        if (!lake.isEnabled()) return;
        var event = json.createObjectNode()
                .put("case_id", trace.caseId())
                .put("event_id", UUID.randomUUID().toString())
                .put("activity", activity)
                .put("timestamp", Instant.now().toString())
                .put("resource", "spring-api")
                .put("status", status)
                .put("sensor_id", trace.sensorId())
                .put("region_id", regionId)
                .put("reading_id", readingId)
                .put("alert_id", alertId)
                .put("source", trace.source());
        var folder = lake.getBasePath().resolve("events");
        try {
            Files.createDirectories(folder);
            Files.writeString(folder.resolve("api.jsonl"), json.writeValueAsString(event) + "\n",
                    StandardCharsets.UTF_8, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (IOException error) {
            LOG.atWarn().addKeyValue("case_id", trace.caseId())
                    .addKeyValue("reason", error.getClass().getSimpleName()).log("process_event_not_recorded");
        }
    }
}
