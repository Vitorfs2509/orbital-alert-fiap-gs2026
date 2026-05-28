package com.orbitalalert.backend.entity;
import jakarta.persistence.*;import java.time.LocalDateTime;
@Entity @Table(name="regions")
public class Region {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @Column(nullable=false) private String name; @Column(nullable=false) private String city; @Column(nullable=false,length=2) private String state;
 @Column(nullable=false) private Double latitude; @Column(nullable=false) private Double longitude;
 @Column(name="satellite_risk_score",nullable=false) private Double satelliteRiskScore=0.0;
 @Enumerated(EnumType.STRING) @Column(name="risk_level",nullable=false) private RiskLevel riskLevel;
 @Column(name="created_at",nullable=false) private LocalDateTime createdAt=LocalDateTime.now();
 public Long getId(){return id;} public void setId(Long id){this.id=id;} public String getName(){return name;} public void setName(String name){this.name=name;}
 public String getCity(){return city;} public void setCity(String city){this.city=city;} public String getState(){return state;} public void setState(String state){this.state=state;}
 public Double getLatitude(){return latitude;} public void setLatitude(Double latitude){this.latitude=latitude;} public Double getLongitude(){return longitude;} public void setLongitude(Double longitude){this.longitude=longitude;}
 public Double getSatelliteRiskScore(){return satelliteRiskScore;} public void setSatelliteRiskScore(Double satelliteRiskScore){this.satelliteRiskScore=satelliteRiskScore;}
 public RiskLevel getRiskLevel(){return riskLevel;} public void setRiskLevel(RiskLevel riskLevel){this.riskLevel=riskLevel;}
 public LocalDateTime getCreatedAt(){return createdAt;} public void setCreatedAt(LocalDateTime createdAt){this.createdAt=createdAt;}
}
