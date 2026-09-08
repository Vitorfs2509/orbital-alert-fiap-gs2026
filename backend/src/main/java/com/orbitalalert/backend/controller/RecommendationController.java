package com.orbitalalert.backend.controller;

import com.orbitalalert.backend.dto.RecommendationDto.PromptResponse;
import com.orbitalalert.backend.dto.RecommendationDto.RecommendationResponse;
import com.orbitalalert.backend.service.RecommendationService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * Recomendacoes de IA generativa como apoio a decisao.
 *
 * <p>Somente leitura: nenhum endpoint aqui cria, altera ou resolve alertas.
 */
@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

    private final RecommendationService service;

    public RecommendationController(RecommendationService service) {
        this.service = service;
    }

    /** Recomendacao para uma regiao, a partir da camada CURATED do Data Lake. */
    @GetMapping("/regions/{regionId}")
    public RecommendationResponse byRegion(@PathVariable Long regionId) {
        return service.forRegion(regionId);
    }

    /** Recomendacao para todas as regioes cadastradas. */
    @GetMapping
    public List<RecommendationResponse> all() {
        return service.forAllRegions();
    }

    /** Prompt exato enviado a IA - util para evidenciar o contexto na avaliacao. */
    @GetMapping("/regions/{regionId}/prompt")
    public PromptResponse prompt(@PathVariable Long regionId) {
        return service.promptForRegion(regionId);
    }
}
