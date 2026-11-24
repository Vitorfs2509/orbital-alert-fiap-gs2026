package com.orbitalalert.backend.controller;

import com.orbitalalert.backend.dto.RecommendationDto.RiskResponse;
import com.orbitalalert.backend.service.RecommendationService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class RiskController {
    private final RecommendationService recommendations;

    public RiskController(RecommendationService recommendations) {
        this.recommendations = recommendations;
    }

    @GetMapping("/api/risk")
    public List<RiskResponse> list() {
        return recommendations.allRisks();
    }
}
