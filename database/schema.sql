-- Orbital Alert - PostgreSQL schema
-- FIAP Global Solution 2026/1 - Space Economy

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'VIEWER'
        CHECK (role IN ('ADMIN', 'ANALYST', 'VIEWER')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    city VARCHAR(120) NOT NULL,
    state CHAR(2) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude NUMERIC(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    satellite_risk_score NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (satellite_risk_score BETWEEN 0 AND 100),
    risk_level VARCHAR(10) NOT NULL
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensors (
    id BIGSERIAL PRIMARY KEY,
    region_id BIGINT NOT NULL,
    type VARCHAR(30) NOT NULL
        CHECK (type IN ('TEMPERATURE', 'WATER_LEVEL', 'SMOKE', 'RAINFALL', 'HUMIDITY')),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')),
    unit VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sensors_regions
        FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    sensor_id BIGINT NOT NULL,
    value NUMERIC(10,2) NOT NULL,
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sensor_readings_sensors
        FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    region_id BIGINT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL
        CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(15) NOT NULL DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'MONITORING', 'RESOLVED')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    CONSTRAINT fk_alerts_regions
        FOREIGN KEY (region_id) REFERENCES regions(id) ON DELETE CASCADE,
    CONSTRAINT chk_alert_resolution CHECK (
        (status = 'RESOLVED' AND resolved_at IS NOT NULL)
        OR (status IN ('OPEN', 'MONITORING') AND resolved_at IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_regions_risk_level ON regions(risk_level);
CREATE INDEX IF NOT EXISTS idx_sensors_region_id ON sensors(region_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_measured_at ON sensor_readings(measured_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_region_id ON alerts(region_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
