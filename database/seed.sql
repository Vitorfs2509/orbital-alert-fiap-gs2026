-- Orbital Alert - seed data
-- Execute schema.sql first.

INSERT INTO users (name, email, password_hash, role) VALUES
('Yuri Zacarioto', 'yuri@orbitalalert.local', 'hash_yuri_123', 'ADMIN'),
('Vitor Sternik', 'vitor.sternik@orbitalalert.local', 'hash_vitor_456', 'ANALYST'),
('Caio Rocha', 'caio.rocha@orbitalalert.local', 'hash_caio_789', 'VIEWER');

INSERT INTO regions (name, city, state, latitude, longitude, satellite_risk_score, risk_level) VALUES
('Margem Rio Tietê - Norte', 'São Paulo', 'SP', -23.500520, -46.624230, 82.50, 'HIGH'),
('Serra da Mantiqueira - Sul', 'Campos do Jordão', 'SP', -22.739180, -45.591930, 68.20, 'MEDIUM'),
('Zona Rural Oeste', 'Campinas', 'SP', -22.923980, -47.067430, 91.10, 'CRITICAL'),
('Área de Preservação Leste', 'Niterói', 'RJ', -22.883240, -43.103410, 44.70, 'LOW');

INSERT INTO sensors (region_id, type, status, unit) VALUES
(1, 'RAIN', 'ACTIVE', 'mm/h'),
(1, 'WATER_LEVEL', 'ACTIVE', 'cm'),
(2, 'HUMIDITY', 'ACTIVE', '%'),
(2, 'TEMPERATURE', 'ACTIVE', '°C'),
(3, 'SMOKE', 'ACTIVE', 'ppm'),
(3, 'TEMPERATURE', 'MAINTENANCE', '°C'),
(4, 'RAIN', 'INACTIVE', 'mm/h');

INSERT INTO sensor_readings (sensor_id, value, measured_at) VALUES
(1, 42.30, CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
(1, 53.10, CURRENT_TIMESTAMP - INTERVAL '15 minutes'),
(2, 188.00, CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
(2, 205.00, CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
(3, 81.50, CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
(4, 34.20, CURRENT_TIMESTAMP - INTERVAL '22 minutes'),
(5, 290.00, CURRENT_TIMESTAMP - INTERVAL '8 minutes'),
(6, 39.80, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
(7, 0.00, CURRENT_TIMESTAMP - INTERVAL '2 hours');

INSERT INTO alerts (region_id, title, description, severity, status, created_at, resolved_at) VALUES
(1, 'Risco de enchente no Tietê', 'Nível do rio acima do esperado e chuva intensa contínua.', 'HIGH', 'OPEN', CURRENT_TIMESTAMP - INTERVAL '40 minutes', NULL),
(3, 'Foco de calor elevado', 'Sensor de fumaça detectou concentração acima do limite seguro.', 'CRITICAL', 'MONITORING', CURRENT_TIMESTAMP - INTERVAL '12 minutes', NULL),
(2, 'Umidade em queda', 'Queda de umidade pode favorecer propagação de incêndio em vegetação seca.', 'MEDIUM', 'OPEN', CURRENT_TIMESTAMP - INTERVAL '1 hour', NULL),
(4, 'Condição normalizada', 'Chuva cessou e risco local voltou ao patamar esperado.', 'LOW', 'RESOLVED', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours 20 minutes');
