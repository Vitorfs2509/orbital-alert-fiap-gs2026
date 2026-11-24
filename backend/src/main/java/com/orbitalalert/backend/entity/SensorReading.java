package com.orbitalalert.backend.entity;
import jakarta.persistence.*;import java.time.LocalDateTime;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
@Entity @Table(name="sensor_readings")
public class SensorReading {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(optional=false) @JoinColumn(name="sensor_id") private Sensor sensor;
 @JdbcTypeCode(SqlTypes.DECIMAL) @Column(nullable=false,precision=10,scale=2) private Double value;
 @Column(name="measured_at",nullable=false) private LocalDateTime measuredAt=LocalDateTime.now();
 public Long getId(){return id;} public void setId(Long id){this.id=id;} public Sensor getSensor(){return sensor;} public void setSensor(Sensor sensor){this.sensor=sensor;}
 public Double getValue(){return value;} public void setValue(Double value){this.value=value;} public LocalDateTime getMeasuredAt(){return measuredAt;} public void setMeasuredAt(LocalDateTime measuredAt){this.measuredAt=measuredAt;}
}
