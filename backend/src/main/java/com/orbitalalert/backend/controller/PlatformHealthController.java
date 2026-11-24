package com.orbitalalert.backend.controller;

import com.orbitalalert.backend.service.PipelineObservability;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class PlatformHealthController {
    private final JdbcTemplate database;
    private final PipelineObservability observability;

    public PlatformHealthController(JdbcTemplate database, PipelineObservability observability) {
        this.database = database;
        this.observability = observability;
    }

    @GetMapping("/api/status")
    public Map<String, Object> status() {
        return observability.status();
    }

    @GetMapping("/api/health")
    public ResponseEntity<Map<String, String>> health() {
        try {
            database.queryForObject("SELECT 1", Integer.class);
            return ResponseEntity.ok(Map.of("status", "UP"));
        } catch (DataAccessException unavailable) {
            return ResponseEntity.status(503).body(Map.of("status", "DOWN"));
        }
    }
}
