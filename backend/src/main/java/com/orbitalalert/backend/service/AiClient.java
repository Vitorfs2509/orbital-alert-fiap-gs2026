package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;

/**
 * Contrato da IA generativa usada como apoio a decisao.
 *
 * <p>A IA nunca executa acoes: ela apenas produz um texto de recomendacao a
 * partir do contexto ja consolidado na camada CURATED do Data Lake. Abrir e
 * resolver alertas continua sendo responsabilidade do
 * {@link AlertService} e do operador humano.
 *
 * <p>Implementacoes: {@link MockAiClient} (padrao, sem dependencia externa) e
 * {@link OpenAiClient} (opcional, habilitado por configuracao).
 */
public interface AiClient {

    /** Identificacao do modo ativo, devolvida na resposta da API (ex.: MOCK). */
    String mode();

    /**
     * @param prompt contexto textual montado por {@link AiPromptBuilder}
     * @param risk   dados estruturados da regiao, para fallback deterministico
     * @return texto de recomendacao em portugues
     */
    String generateRecommendation(String prompt, RegionRisk risk);
}
