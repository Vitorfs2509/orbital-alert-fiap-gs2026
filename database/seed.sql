-- Orbital Alert - seed data for academic demos
-- Execute database/schema.sql before this file.

INSERT INTO users (id, name, email, password_hash, role) VALUES
(1, 'Yuri Monteiro Zacarioto', 'yuri@orbitalalert.local', '$2a$10$mockhashyuri', 'ADMIN'),
(2, 'Vitor Futida Sternik', 'vitor.sternik@orbitalalert.local', '$2a$10$mockhashvitor', 'ANALYST'),
(3, 'Caio Henrique Rocha da Silva', 'caio.rocha@orbitalalert.local', '$2a$10$mockhashcaio', 'VIEWER')
ON CONFLICT (id) DO NOTHING;

INSERT INTO regions (id, name, city, state, latitude, longitude, satellite_risk_score, risk_level) VALUES
(1, 'Margem Rio Tietê - Norte', 'São Paulo', 'SP', -23.500520, -46.624230, 82.50, 'HIGH'),
(2, 'Serra da Mantiqueira - Sul', 'Campos do Jordão', 'SP', -22.739180, -45.591930, 68.20, 'MEDIUM'),
(3, 'Zona Rural Oeste', 'Campinas', 'SP', -22.923980, -47.067430, 91.10, 'CRITICAL'),
(4, 'Área de Preservação Leste', 'Niterói', 'RJ', -22.883240, -43.103410, 44.70, 'LOW')
ON CONFLICT (id) DO NOTHING;

INSERT INTO sensors (id, region_id, type, status, unit) VALUES
(1, 1, 'RAINFALL', 'ACTIVE', 'mm'),
(2, 1, 'WATER_LEVEL', 'ACTIVE', '%'),
(3, 2, 'HUMIDITY', 'ACTIVE', '%'),
(4, 2, 'TEMPERATURE', 'ACTIVE', '°C'),
(5, 3, 'SMOKE', 'ACTIVE', 'index'),
(6, 3, 'TEMPERATURE', 'MAINTENANCE', '°C'),
(7, 4, 'RAINFALL', 'INACTIVE', 'mm')
ON CONFLICT (id) DO NOTHING;

INSERT INTO sensor_readings (sensor_id, value, measured_at) VALUES
(1, 42.30, CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
(1, 63.10, CURRENT_TIMESTAMP - INTERVAL '15 minutes'),
(2, 78.00, CURRENT_TIMESTAMP - INTERVAL '30 minutes'),
(2, 86.40, CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
(3, 81.50, CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
(4, 41.20, CURRENT_TIMESTAMP - INTERVAL '22 minutes'),
(5, 74.00, CURRENT_TIMESTAMP - INTERVAL '8 minutes'),
(6, 39.80, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
(7, 0.00, CURRENT_TIMESTAMP - INTERVAL '2 hours');

INSERT INTO alerts (id, region_id, title, description, severity, status, created_at, resolved_at) VALUES
(1, 1, 'Risco de enchente no Rio Tietê', 'Nível de água elevado e chuva intensa na região monitorada.', 'HIGH', 'OPEN', CURRENT_TIMESTAMP - INTERVAL '40 minutes', NULL),
(2, 3, 'Foco de fumaça em área rural', 'Sensor de fumaça detectou índice acima do limite seguro.', 'CRITICAL', 'MONITORING', CURRENT_TIMESTAMP - INTERVAL '12 minutes', NULL),
(3, 2, 'Temperatura elevada na serra', 'Temperatura acima do esperado aumenta risco de queimadas em vegetação seca.', 'MEDIUM', 'OPEN', CURRENT_TIMESTAMP - INTERVAL '1 hour', NULL),
(4, 4, 'Condição normalizada', 'Chuva cessou e a região voltou ao acompanhamento de rotina.', 'LOW', 'RESOLVED', CURRENT_TIMESTAMP - INTERVAL '3 hours', CURRENT_TIMESTAMP - INTERVAL '2 hours 20 minutes')
ON CONFLICT (id) DO NOTHING;
