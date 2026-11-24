package com.orbitalalert.backend.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;
import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Integracao opcional com um LLM externo compativel com a API de chat da OpenAI.
 *
 * <p>Desativada por padrao. Para habilitar:
 * <pre>
 *   set OPENAI_API_KEY=...        (variavel de ambiente, nunca no codigo)
 *   set AI_PROVIDER=openai
 * </pre>
 *
 * <p>Se a chave nao estiver presente ou a chamada externa falhar, o cliente
 * degrada automaticamente para o {@link MockAiClient}. Assim, uma indisponibilidade
 * de servico externo nunca quebra o build, os testes ou a demonstracao.
 */
@Component
@ConditionalOnProperty(name = "orbital.ai.provider", havingValue = "openai")
public class OpenAiClient implements AiClient {

    private static final Logger log = LoggerFactory.getLogger(OpenAiClient.class);

    private final ObjectMapper json = new ObjectMapper();
    private final MockAiClient fallback = new MockAiClient();
    private final RestClient restClient;

    private final String apiKey;
    private final String model;

    public OpenAiClient(
            RestClient.Builder restClientBuilder,
            @Value("${orbital.ai.base-url:https://api.openai.com/v1}") String baseUrl,
            @Value("${orbital.ai.api-key:}") String apiKey,
            @Value("${orbital.ai.model:gpt-4o-mini}") String model) {
        var http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build();
        var requests = new JdkClientHttpRequestFactory(http);
        requests.setReadTimeout(Duration.ofSeconds(6));
        this.restClient = restClientBuilder.baseUrl(baseUrl).requestFactory(requests).build();
        this.apiKey = apiKey == null ? "" : apiKey.trim();
        this.model = model;

        if (this.apiKey.isEmpty()) {
            log.warn("orbital.ai.provider=openai mas nenhuma API key foi configurada "
                    + "(OPENAI_API_KEY). As recomendacoes continuarao em modo MOCK.");
        }
    }

    @Override
    public String mode() {
        return apiKey.isEmpty() ? "MOCK_FALLBACK_SEM_API_KEY" : "OPENAI:" + model;
    }

    @Override
    public Recommendation generateRecommendation(String prompt, RegionRisk risk) {
        if (apiKey.isEmpty()) {
            return fallback(prompt, risk, mode());
        }
        try {
            String body = json.writeValueAsString(Map.of(
                    "model", model,
                    "temperature", 0.3,
                    "messages", List.of(
                            Map.of("role", "system", "content", AiPromptBuilder.SYSTEM_INSTRUCTION),
                            Map.of("role", "user", "content", prompt))));

            JsonNode response = restClient.post()
                    .uri("/chat/completions")
                    .header("Authorization", "Bearer " + apiKey)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(JsonNode.class);

            String content = response == null ? null
                    : response.path("choices").path(0).path("message").path("content").asText(null);

            if (content == null || content.isBlank()) {
                log.warn("Resposta vazia do provedor de IA; usando modo MOCK.");
                return fallback(prompt, risk, "MOCK_FALLBACK_RESPOSTA_VAZIA");
            }
            return new Recommendation(content.trim(), mode());

        } catch (Exception e) {
            log.warn("Falha ao consultar o provedor de IA ({}); usando modo MOCK.", e.getClass().getSimpleName());
            return fallback(prompt, risk, "MOCK_FALLBACK_ERRO_PROVEDOR");
        }
    }

    private Recommendation fallback(String prompt, RegionRisk risk, String mode) {
        return new Recommendation(fallback.generateRecommendation(prompt, risk).text(), mode);
    }
}
