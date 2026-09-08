package com.orbitalalert.backend.service;

import com.orbitalalert.backend.dto.RecommendationDto.RegionIndicator;
import com.orbitalalert.backend.dto.RecommendationDto.RegionRisk;
import org.springframework.stereotype.Component;

/**
 * Monta o contexto textual enviado a IA generativa.
 *
 * <p>Todo o conteudo vem da camada CURATED do Data Lake: regiao, sensores
 * relevantes, valores atuais, agregacoes, tendencia, score, tipo e nivel de
 * risco. O prompt e exposto em
 * {@code GET /api/recommendations/regions/{id}/prompt} para auditoria.
 */
@Component
public class AiPromptBuilder {

    public static final String SYSTEM_INSTRUCTION = """
            Voce e um analista de defesa civil do sistema Orbital Alert.
            Escreva uma recomendacao objetiva em portugues do Brasil, com no maximo 5 frases,
            para a equipe que monitora a regiao descrita.
            Regras:
            - baseie-se exclusivamente nos dados fornecidos;
            - nao invente medicoes, previsoes ou numeros que nao estejam no contexto;
            - a recomendacao e apoio a decisao: sugira acoes para operadores humanos,
              nunca afirme que alguma acao ja foi executada automaticamente;
            - se o risco for baixo, recomende apenas monitoramento.
            """;

    public String build(RegionRisk risk) {
        StringBuilder prompt = new StringBuilder();

        prompt.append("CONTEXTO DA REGIAO MONITORADA\n");
        prompt.append("Regiao: ").append(risk.regionName())
                .append(" (id ").append(risk.regionId()).append(")\n");
        prompt.append("Score de risco: ").append(risk.riskScore()).append("/100\n");
        prompt.append("Nivel de risco: ").append(risk.riskLevel()).append("\n");
        prompt.append("Tipo de risco: ").append(risk.riskType()).append("\n");
        prompt.append("Sensor dominante: ").append(nullSafe(risk.dominantSensorType())).append("\n");
        prompt.append("Leituras consideradas: ").append(nullSafe(risk.readings()))
                .append(" de ").append(nullSafe(risk.sensors())).append(" sensor(es)\n");
        prompt.append("Janela analisada: ").append(nullSafe(risk.windowStart()))
                .append(" ate ").append(nullSafe(risk.windowEnd())).append("\n");

        prompt.append("\nINDICADORES POR SENSOR\n");
        if (risk.indicators() == null || risk.indicators().isEmpty()) {
            prompt.append("- Nenhum indicador com regra de risco disponivel para esta regiao.\n");
        } else {
            for (RegionIndicator indicator : risk.indicators()) {
                prompt.append("- ").append(indicator.sensorType())
                        .append(": atual ").append(indicator.lastValue()).append(" ").append(indicator.unit())
                        .append(" | media ").append(indicator.avgValue())
                        .append(" | min ").append(indicator.minValue())
                        .append(" | max ").append(indicator.maxValue())
                        .append(" | limiar de alerta ").append(indicator.threshold())
                        .append(" | tendencia de risco ").append(traduzTendencia(indicator.trend()))
                        .append(" | sub-score ").append(indicator.subScore()).append("/100")
                        .append("\n");
            }
        }

        if (risk.ignoredSensorTypes() != null && !risk.ignoredSensorTypes().isEmpty()) {
            prompt.append("\nSensores sem regra de risco definida (ignorados no score): ")
                    .append(String.join(", ", risk.ignoredSensorTypes())).append("\n");
        }

        prompt.append("\nPERGUNTA\n");
        prompt.append("Qual a recomendacao de acao para a equipe de resposta desta regiao?\n");

        return prompt.toString();
    }

    private String traduzTendencia(String trend) {
        if (trend == null) {
            return "desconhecida";
        }
        return switch (trend) {
            case "RISING" -> "em elevacao";
            case "FALLING" -> "em queda";
            case "STABLE" -> "estavel";
            case "INSUFFICIENT_DATA" -> "dados insuficientes";
            default -> trend;
        };
    }

    private String nullSafe(Object value) {
        return value == null ? "nao informado" : String.valueOf(value);
    }
}
