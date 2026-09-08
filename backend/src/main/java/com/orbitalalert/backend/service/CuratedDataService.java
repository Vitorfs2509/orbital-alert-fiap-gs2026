package com.orbitalalert.backend.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;

/**
 * Le a camada CURATED (Gold) do Data Lake.
 *
 * <p>Fonte primaria da IA generativa: o arquivo
 * {@code data-lake/curated/region_risk_latest.json}, produzido por
 * {@code etl/trusted_to_curated.py}. Se o arquivo ainda nao existir (ETL nunca
 * executado), o {@link RecommendationService} recorre ao banco operacional e
 * sinaliza isso na resposta.
 */
@Service
public class CuratedDataService {

    private static final Logger log = LoggerFactory.getLogger(CuratedDataService.class);
    private static final String CURATED_FILE = "region_risk_latest.json";

    private final ObjectMapper json = JsonMapper.builder().addModule(new JavaTimeModule()).build();
    private final DataLakeService dataLake;

    public CuratedDataService(DataLakeService dataLake) {
        this.dataLake = dataLake;
    }

    public Path curatedFile() {
        return dataLake.getBasePath().resolve("curated").resolve(CURATED_FILE);
    }

    public boolean isAvailable() {
        return Files.isReadable(curatedFile());
    }

    /** Todas as regioes presentes na camada CURATED (lista vazia se indisponivel). */
    public List<RegionRisk> findAll() {
        Path file = curatedFile();
        if (!Files.isReadable(file)) {
            log.debug("Camada CURATED indisponivel em {}", file);
            return List.of();
        }
        try {
            return json.readValue(Files.readString(file), new TypeReference<List<RegionRisk>>() {
            });
        } catch (Exception e) {
            log.warn("Falha ao ler a camada CURATED em {}: {}", file, e.toString());
            return List.of();
        }
    }

    public Optional<RegionRisk> findByRegionId(Long regionId) {
        return findAll().stream()
                .filter(risk -> regionId.equals(risk.regionId()))
                .findFirst();
    }
}
