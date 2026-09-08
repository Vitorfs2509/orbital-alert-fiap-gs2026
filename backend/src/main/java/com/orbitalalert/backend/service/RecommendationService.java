package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RecommendationDto.PromptResponse;
import com.orbitalalert.backend.dto.RecommendationDto.RecommendationResponse;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import com.orbitalalert.backend.entity.Region;
import com.orbitalalert.backend.entity.SensorReading;
import com.orbitalalert.backend.exception.NotFoundException;
import com.orbitalalert.backend.repository.RegionRepository;
import com.orbitalalert.backend.repository.SensorReadingRepository;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Gera recomendacoes de apoio a decisao a partir do Data Lake.
 *
 * <p>Fluxo: sensor -> API -> RAW -> ETL -> TRUSTED -> ETL -> CURATED -> IA.
 *
 * <p>A camada CURATED e a fonte primaria do contexto enviado a IA. O banco
 * operacional so e consultado quando o ETL ainda nao foi executado, e nesse
 * caso a resposta sinaliza {@code dataSource=OPERATIONAL_DB_FALLBACK} para que
 * a origem do dado fique explicita na demonstracao.
 *
 * <p>A IA e estritamente consultiva: nao cria, altera nem resolve alertas.
 */
@Service
public class RecommendationService {

    /** Origem do contexto usado na recomendacao. */
    public static final String SOURCE_CURATED = "CURATED_LAYER";
    public static final String SOURCE_DB = "OPERATIONAL_DB_FALLBACK";

    private final CuratedDataService curated;
    private final RegionRepository regionRepo;
    private final SensorReadingRepository readingRepo;
    private final RiskScoreCalculator calculator;
    private final AiPromptBuilder promptBuilder;
    private final AiClient aiClient;

    public RecommendationService(CuratedDataService curated, RegionRepository regionRepo,
                                 SensorReadingRepository readingRepo, RiskScoreCalculator calculator,
                                 AiPromptBuilder promptBuilder, ObjectProvider<AiClient> aiClientProvider) {
        this.curated = curated;
        this.regionRepo = regionRepo;
        this.readingRepo = readingRepo;
        this.calculator = calculator;
        this.promptBuilder = promptBuilder;
        // Garante que o modo MOCK funcione mesmo sem nenhum cliente configurado:
        // nenhuma dependencia externa pode impedir a demonstracao.
        this.aiClient = aiClientProvider.getIfAvailable(MockAiClient::new);
    }

    /** Contexto de risco resolvido e a camada de onde ele veio. */
    private record ResolvedRisk(RegionRisk risk, String dataSource) {
    }

    public RecommendationResponse forRegion(Long regionId) {
        ResolvedRisk resolved = resolve(regionId);
        RegionRisk risk = resolved.risk();

        String prompt = promptBuilder.build(risk);
        String recommendation = aiClient.generateRecommendation(prompt, risk);

        return new RecommendationResponse(
                risk.regionId(), risk.regionName(), risk.riskScore(), risk.riskLevel(), risk.riskType(),
                recommendation, LocalDateTime.now(), aiClient.mode(), resolved.dataSource(), risk);
    }

    public List<RecommendationResponse> forAllRegions() {
        return regionRepo.findAll().stream()
                .map(region -> forRegion(region.getId()))
                .toList();
    }

    /** Devolve o prompt exato que seria enviado a IA, para auditoria academica. */
    public PromptResponse promptForRegion(Long regionId) {
        ResolvedRisk resolved = resolve(regionId);
        return new PromptResponse(regionId, resolved.dataSource(), aiClient.mode(),
                promptBuilder.build(resolved.risk()));
    }

    /**
     * Resolve o contexto de risco priorizando a camada CURATED do Data Lake.
     *
     * <p>1) {@code data-lake/curated/region_risk_latest.json} (gerado pelo ETL);
     * <p>2) fallback: agregacao das leituras do banco operacional.
     */
    private ResolvedRisk resolve(Long regionId) {
        Region region = regionRepo.findById(regionId)
                .orElseThrow(() -> new NotFoundException("Região não encontrada"));

        Optional<RegionRisk> fromLake = curated.findByRegionId(regionId);
        if (fromLake.isPresent()) {
            return new ResolvedRisk(withRegionName(fromLake.get(), region), SOURCE_CURATED);
        }

        List<SensorReading> readings = readingRepo.findBySensorRegionIdOrderByMeasuredAtAsc(regionId);
        return new ResolvedRisk(calculator.fromReadings(region, readings), SOURCE_DB);
    }

    /** O nome cadastrado no banco prevalece sobre o nome do arquivo de referencia. */
    private RegionRisk withRegionName(RegionRisk risk, Region region) {
        if (region.getName() == null || region.getName().equals(risk.regionName())) {
            return risk;
        }
        return new RegionRisk(risk.regionId(), region.getName(), risk.riskScore(), risk.riskLevel(),
                risk.riskType(), risk.dominantSensorType(), risk.readings(), risk.sensors(),
                risk.windowStart(), risk.windowEnd(), risk.indicators(), risk.ignoredSensorTypes(),
                risk.generatedAt());
    }
}
