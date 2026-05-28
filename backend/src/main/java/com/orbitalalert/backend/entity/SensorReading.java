package com.orbitalalert.backend.entity;
import jakarta.persistence.*;import java.time.LocalDateTime;
@Entity @Table(name="sensor_readings")
public class SensorReading {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(optional=false) @JoinColumn(name="sensor_id") private Sensor sensor;
 @Column(nullable=false) private Double value;
 @Column(name="measured_at",nullable=false) private LocalDateTime measuredAt=LocalDateTime.now();
 public Long getId(){return id;} public void setId(Long id){this.id=id;} public Sensor getSensor(){return sensor;} public void setSensor(Sensor sensor){this.sensor=sensor;}
 public Double getValue(){return value;} public void setValue(Double value){this.value=value;} public LocalDateTime getMeasuredAt(){return measuredAt;} public void setMeasuredAt(LocalDateTime measuredAt){this.measuredAt=measuredAt;}
}
