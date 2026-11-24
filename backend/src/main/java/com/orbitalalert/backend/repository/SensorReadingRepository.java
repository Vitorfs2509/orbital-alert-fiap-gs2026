package com.orbitalalert.backend.repository;
import com.orbitalalert.backend.entity.SensorReading;import org.springframework.data.jpa.repository.JpaRepository;import org.springframework.data.jpa.repository.Query;import java.util.List;
public interface SensorReadingRepository extends JpaRepository<SensorReading,Long>{
 @Query("""
     SELECT reading FROM SensorReading reading
     WHERE NOT EXISTS (
         SELECT newer.id FROM SensorReading newer
         WHERE newer.sensor.id = reading.sensor.id
           AND (newer.measuredAt > reading.measuredAt
                OR (newer.measuredAt = reading.measuredAt AND newer.id > reading.id))
     ) ORDER BY reading.sensor.id
     """)
 List<SensorReading> findLatestPerSensor();
 // Usado pelo RecommendationService quando a camada CURATED ainda nao foi gerada.
 List<SensorReading> findBySensorRegionIdOrderByMeasuredAtAsc(Long regionId);
}
