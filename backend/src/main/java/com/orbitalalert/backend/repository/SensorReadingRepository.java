package com.orbitalalert.backend.repository;
import com.orbitalalert.backend.entity.SensorReading;import org.springframework.data.jpa.repository.JpaRepository;import org.springframework.data.jpa.repository.Query;import java.util.List;
public interface SensorReadingRepository extends JpaRepository<SensorReading,Long>{
 @Query("SELECT sr FROM SensorReading sr WHERE sr.measuredAt IN (SELECT MAX(s2.measuredAt) FROM SensorReading s2 GROUP BY s2.sensor.id)")
 List<SensorReading> findLatestPerSensor();
 // Usado pelo RecommendationService quando a camada CURATED ainda nao foi gerada.
 List<SensorReading> findBySensorRegionIdOrderByMeasuredAtAsc(Long regionId);
}
