package com.orbitalalert.backend.entity;
import jakarta.persistence.*;import java.time.LocalDateTime;
@Entity @Table(name="sensors")
public class Sensor {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(optional=false) @JoinColumn(name="region_id") private Region region;
 @Enumerated(EnumType.STRING) @Column(nullable=false) private SensorType type;
 @Enumerated(EnumType.STRING) @Column(nullable=false) private SensorStatus status;
 @Column(nullable=false) private String unit;
 @Column(name="created_at",nullable=false) private LocalDateTime createdAt=LocalDateTime.now();
 public Long getId(){return id;} public void setId(Long id){this.id=id;} public Region getRegion(){return region;} public void setRegion(Region region){this.region=region;}
 public SensorType getType(){return type;} public void setType(SensorType type){this.type=type;} public SensorStatus getStatus(){return status;} public void setStatus(SensorStatus status){this.status=status;}
 public String getUnit(){return unit;} public void setUnit(String unit){this.unit=unit;} public LocalDateTime getCreatedAt(){return createdAt;} public void setCreatedAt(LocalDateTime createdAt){this.createdAt=createdAt;}
}
