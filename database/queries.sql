-- Orbital Alert - useful queries

-- 1) List active alerts (open or monitoring)
SELECT
    a.id,
    r.name AS region_name,
    a.title,
    a.severity,
    a.status,
    a.created_at
FROM alerts a
JOIN regions r ON r.id = a.region_id
WHERE a.status IN ('OPEN', 'MONITORING')
ORDER BY a.created_at DESC;

-- 2) List sensors by region
SELECT
    r.id AS region_id,
    r.name AS region_name,
    s.id AS sensor_id,
    s.type,
    s.status,
    s.unit
FROM regions r
LEFT JOIN sensors s ON s.region_id = r.id
ORDER BY r.id, s.id;

-- 3) List latest readings (one latest value per sensor)
SELECT
    s.id AS sensor_id,
    s.type,
    r.name AS region_name,
    sr.value,
    sr.measured_at
FROM sensors s
JOIN regions r ON r.id = s.region_id
JOIN LATERAL (
    SELECT value, measured_at
    FROM sensor_readings
    WHERE sensor_id = s.id
    ORDER BY measured_at DESC
    LIMIT 1
) sr ON TRUE
ORDER BY sr.measured_at DESC;

-- 4) Count alerts by severity
SELECT
    severity,
    COUNT(*) AS total_alerts
FROM alerts
GROUP BY severity
ORDER BY total_alerts DESC, severity;

-- 5) Find high-risk regions
SELECT
    id,
    name,
    city,
    state,
    satellite_risk_score,
    risk_level
FROM regions
WHERE risk_level IN ('HIGH', 'CRITICAL')
   OR satellite_risk_score >= 70
ORDER BY satellite_risk_score DESC;

-- 6) Update an alert as resolved (replace :alert_id)
-- Example: UPDATE alerts ... WHERE id = 1;
UPDATE alerts
SET status = 'RESOLVED',
    resolved_at = CURRENT_TIMESTAMP
WHERE id = :alert_id
  AND status <> 'RESOLVED';
