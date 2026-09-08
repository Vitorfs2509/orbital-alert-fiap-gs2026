package com.orbitalalert.backend.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.orbitalalert.backend.dto.RawEventDto;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * Escreve os eventos brutos na camada RAW (Bronze) do Data Lake.
 *
 * <p>Formato: um arquivo JSON Lines por dia, particionado por data:
 * {@code data-lake/raw/YYYY/MM/DD/readings-YYYY-MM-DD.jsonl}.
 *
 * <p>A gravacao no Data Lake e sempre secundaria: qualquer falha de filesystem
 * e registrada em log e nunca interrompe a persistencia da leitura no banco
 * operacional nem a geracao de alertas.
 */
@Service
public class DataLakeService {

    private static final Logger log = LoggerFactory.getLogger(DataLakeService.class);
    private static final DateTimeFormatter PARTITION = DateTimeFormatter.ofPattern("yyyy/MM/dd");

    /** ObjectMapper proprio: garante uma linha por evento, independente da config global. */
    private final ObjectMapper json = JsonMapper.builder()
            .addModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .disable(SerializationFeature.INDENT_OUTPUT)
            .build();

    private final Path basePath;
    private final boolean enabled;

    public DataLakeService(
            @Value("${orbital.datalake.base-path:../data-lake}") String configuredPath,
            @Value("${orbital.datalake.enabled:true}") boolean enabled) {
        this.enabled = enabled;
        this.basePath = resolveBasePath(configuredPath);
        log.info("Data Lake {} | base-path: {}", enabled ? "habilitado" : "desabilitado", this.basePath);
    }

    /**
     * Resolve o caminho configurado sem depender de uma maquina especifica.
     *
     * <p>Aceita caminho absoluto (via property ou variavel de ambiente
     * {@code DATA_LAKE_PATH}). Sendo relativo, testa os candidatos usuais para
     * funcionar tanto rodando de {@code backend/} (mvnw spring-boot:run) quanto
     * da raiz do repositorio (java -jar).
     */
    private static Path resolveBasePath(String configuredPath) {
        Path configured = Paths.get(configuredPath);
        if (configured.isAbsolute()) {
            return configured.normalize();
        }
        for (String candidate : new String[]{configuredPath, "data-lake", "../data-lake"}) {
            Path path = Paths.get(candidate).toAbsolutePath().normalize();
            if (Files.isDirectory(path)) {
                return path;
            }
        }
        return configured.toAbsolutePath().normalize();
    }

    /** Grava um evento bruto na camada RAW. Nunca lanca excecao para o chamador. */
    public void writeRawEvent(RawEventDto event) {
        if (!enabled) {
            return;
        }
        try {
            LocalDate day = event.receivedAt().toLocalDate();
            Path directory = basePath.resolve("raw").resolve(PARTITION.format(day));
            Files.createDirectories(directory);

            Path file = directory.resolve("readings-" + day + ".jsonl");
            String line = json.writeValueAsString(event) + System.lineSeparator();
            Files.writeString(file, line, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);

        } catch (IOException | RuntimeException e) {
            log.warn("Falha ao gravar evento na camada RAW do Data Lake (fluxo operacional preservado): {}",
                    e.toString());
        }
    }

    /** Raiz do Data Lake, usada tambem pela leitura da camada CURATED. */
    public Path getBasePath() {
        return basePath;
    }

    public boolean isEnabled() {
        return enabled;
    }
}
