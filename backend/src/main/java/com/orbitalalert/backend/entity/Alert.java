package com.orbitalalert.backend.entity;
import jakarta.persistence.*;import java.time.LocalDateTime;
@Entity @Table(name="alerts")
public class Alert {
 @Id @GeneratedValue(strategy=GenerationType.IDENTITY) private Long id;
 @ManyToOne(optional=false) @JoinColumn(name="region_id") private Region region;
 @Column(nullable=false) private String title;
 @Column(nullable=false,length=500) private String description;
 @Enumerated(EnumType.STRING) @Column(nullable=false) private RiskLevel severity;
 @Enumerated(EnumType.STRING) @Column(nullable=false) private AlertStatus status=AlertStatus.OPEN;
 @Column(name="created_at",nullable=false) private LocalDateTime createdAt=LocalDateTime.now();
 @Column(name="resolved_at") private LocalDateTime resolvedAt;
 public Long getId(){return id;} public void setId(Long id){this.id=id;} public Region getRegion(){return region;} public void setRegion(Region region){this.region=region;}
 public String getTitle(){return title;} public void setTitle(String title){this.title=title;} public String getDescription(){return description;} public void setDescription(String description){this.description=description;}
 public RiskLevel getSeverity(){return severity;} public void setSeverity(RiskLevel severity){this.severity=severity;} public AlertStatus getStatus(){return status;} public void setStatus(AlertStatus status){this.status=status;}
 public LocalDateTime getCreatedAt(){return createdAt;} public void setCreatedAt(LocalDateTime createdAt){this.createdAt=createdAt;} public LocalDateTime getResolvedAt(){return resolvedAt;} public void setResolvedAt(LocalDateTime resolvedAt){this.resolvedAt=resolvedAt;}
}
