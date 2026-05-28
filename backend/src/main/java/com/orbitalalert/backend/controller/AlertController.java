package com.orbitalalert.backend.controller;

import com.orbitalalert.backend.dto.AlertDto;
import com.orbitalalert.backend.service.AlertService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/alerts")
public class AlertController {
    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @GetMapping
    public List<AlertDto> list() {
        return alertService.list();
    }

    @GetMapping("/active")
    public List<AlertDto> active() {
        return alertService.active();
    }

    @PutMapping("/{id}/resolve")
    public AlertDto resolve(@PathVariable Long id) {
        return alertService.resolve(id);
    }
}
