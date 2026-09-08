package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RecommendationDto.RegionIndicator;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * Modo MOCK da IA generativa: o padrao do projeto.
 *
 * <p>Funciona integralmente offline, sem API key e sem chamada de rede, para
 * que build, testes e demonstracao academica nunca dependam de servico externo.
 * O texto e composto a partir do mesmo contexto CURATED que seria enviado a um
 * LLM, seguindo um roteiro fixo por nivel e tipo de risco.
 *
 * <p>Ativo quando {@code orbital.ai.provider=mock} ou quando a propriedade nao
 * esta definida.
 */
@Component
@ConditionalOnProperty(name = "orbital.ai.provider", havingValue = "mock", matchIfMissing = true)
public class MockAiClient implements AiClient {

    @Override
    public String mode() {
        return "MOCK";
    }

    @Override
    public String generateRecommendation(String prompt, RegionRisk risk) {
        StringBuilder text = new StringBuilder();
        text.append(abertura(risk));
        text.append(" ").append(evidencia(risk));
        text.append(" ").append(acoes(risk));
        text.append(" Esta recomendacao e apoio a decisao: a execucao das acoes cabe a equipe responsavel.");
        return text.toString();
    }

    private String abertura(RegionRisk risk) {
        String regiao = risk.regionName() == null ? "a regiao monitorada" : risk.regionName();
        return switch (nivel(risk)) {
            case "HIGH" -> String.format(
                    "Risco ALTO em %s: score %d/100 com indicacao de %s.",
                    regiao, score(risk), descreveTipo(risk.riskType()));
            case "MEDIUM" -> String.format(
                    "Risco MODERADO em %s: score %d/100 com sinais de %s.",
                    regiao, score(risk), descreveTipo(risk.riskType()));
            default -> String.format(
                    "Risco BAIXO em %s: score %d/100, sem evidencia de evento critico em formacao.",
                    regiao, score(risk));
        };
    }

    private String evidencia(RegionRisk risk) {
        RegionIndicator dominante = dominante(risk);
        if (dominante == null) {
            return "Nao ha indicadores com regra de risco associada na janela analisada.";
        }
        return String.format(
                "O indicador determinante e %s, com leitura atual de %s %s e media de %s frente ao limiar de alerta de %s, tendencia %s.",
                dominante.sensorType(), dominante.lastValue(), dominante.unit(),
                dominante.avgValue(), dominante.threshold(), tendencia(dominante.trend()));
    }

    private String acoes(RegionRisk risk) {
        String tipo = risk.riskType() == null ? "NONE" : risk.riskType();
        return switch (nivel(risk)) {
            case "HIGH" -> "FLOOD".equals(tipo)
                    ? "Acoes sugeridas: acionar a defesa civil, comunicar moradores das areas ribeirinhas, "
                    + "avaliar rotas de evacuacao e ampliar a frequencia de leitura dos sensores de nivel e chuva."
                    : "Acoes sugeridas: acionar brigada de incendio e defesa civil, restringir acesso a area, "
                    + "verificar focos de calor por imagem de satelite e ampliar a frequencia de leitura dos sensores.";
            case "MEDIUM" -> "FLOOD".equals(tipo)
                    ? "Acoes sugeridas: colocar a equipe em prontidao, revisar a drenagem local e reavaliar a regiao "
                    + "a cada nova janela de leituras."
                    : "Acoes sugeridas: colocar a equipe em prontidao, reforcar a vigilancia de focos de calor e "
                    + "reavaliar a regiao a cada nova janela de leituras.";
            default -> "Acao sugerida: manter o monitoramento de rotina, sem necessidade de mobilizacao adicional.";
        };
    }

    private RegionIndicator dominante(RegionRisk risk) {
        if (risk.indicators() == null || risk.indicators().isEmpty()) {
            return null;
        }
        return risk.indicators().get(0);
    }

    private String descreveTipo(String riskType) {
        if (riskType == null) {
            return "risco ambiental nao classificado";
        }
        return switch (riskType) {
            case "FLOOD" -> "risco hidrologico (enchente)";
            case "FIRE" -> "risco de incendio";
            case "NONE" -> "condicao dentro do esperado";
            default -> riskType;
        };
    }

    private String tendencia(String trend) {
        if (trend == null) {
            return "desconhecida";
        }
        return switch (trend) {
            case "RISING" -> "de elevacao do risco";
            case "FALLING" -> "de reducao do risco";
            case "STABLE" -> "estavel";
            case "INSUFFICIENT_DATA" -> "indefinida por falta de amostras";
            default -> trend;
        };
    }

    private String nivel(RegionRisk risk) {
        return risk.riskLevel() == null ? "LOW" : risk.riskLevel();
    }

    private int score(RegionRisk risk) {
        return risk.riskScore() == null ? 0 : risk.riskScore();
    }
}
