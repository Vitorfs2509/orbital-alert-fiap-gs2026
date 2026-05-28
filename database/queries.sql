-- Orbital Alert - useful demonstration queries

-- 1) Listar alertas ativos
SELECT
    a.id,
    r.name AS region_name,
    r.city,
    r.state,
    a.title,
    a.severity,
    a.status,
    a.created_at
FROM alerts a
JOIN regions r ON r.id = a.region_id
WHERE a.status IN ('OPEN', 'MONITORING')
ORDER BY a.created_at DESC;

-- 2) Listar sensores por região
SELECT
    r.id AS region_id,
    r.name AS region_name,
    s.id AS sensor_id,
    s.type,
    s.status,
    s.unit
FROM regions r
LEFT JOIN sensors s ON s.region_id = r.id
ORDER BY r.name, s.type;

-- 3) Listar histórico de leituras simuladas
SELECT
    sr.id AS reading_id,
    r.name AS region_name,
    s.type AS sensor_type,
    sr.value,
    s.unit,
    sr.measured_at
FROM sensor_readings sr
JOIN sensors s ON s.id = sr.sensor_id
JOIN regions r ON r.id = s.region_id
ORDER BY sr.measured_at DESC;

-- 4) Listar a leitura mais recente de cada sensor
SELECT DISTINCT ON (s.id)
    s.id AS sensor_id,
    r.name AS region_name,
    s.type,
    sr.value,
    s.unit,
    sr.measured_at
FROM sensors s
JOIN regions r ON r.id = s.region_id
JOIN sensor_readings sr ON sr.sensor_id = s.id
ORDER BY s.id, sr.measured_at DESC;

-- 5) Contar alertas por severidade
SELECT
    severity,
    COUNT(*) AS total_alerts
FROM alerts
GROUP BY severity
ORDER BY total_alerts DESC, severity;

-- 6) Buscar regiões com risco alto ou crítico
SELECT
    id,
    name,
    city,
    state,
    satellite_risk_score,
    risk_level
FROM regions
WHERE risk_level IN ('HIGH', 'CRITICAL')
ORDER BY satellite_risk_score DESC;

-- 7) Resumo de monitoramento por região
SELECT
    r.id,
    r.name,
    r.risk_level,
    r.satellite_risk_score,
    COUNT(DISTINCT s.id) AS total_sensors,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status IN ('OPEN', 'MONITORING')) AS active_alerts
FROM regions r
LEFT JOIN sensors s ON s.region_id = r.id
LEFT JOIN alerts a ON a.region_id = r.id
GROUP BY r.id, r.name, r.risk_level, r.satellite_risk_score
ORDER BY r.satellite_risk_score DESC;
