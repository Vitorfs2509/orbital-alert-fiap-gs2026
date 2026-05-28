package com.orbitalalert.backend.repository;
import com.orbitalalert.backend.entity.Sensor;import org.springframework.data.jpa.repository.JpaRepository;
public interface SensorRepository extends JpaRepository<Sensor,Long>{}
