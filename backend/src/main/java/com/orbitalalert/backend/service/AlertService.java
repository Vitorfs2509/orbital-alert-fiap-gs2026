package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.AlertDto;import com.orbitalalert.backend.entity.*;import com.orbitalalert.backend.exception.NotFoundException;import com.orbitalalert.backend.repository.AlertRepository;import org.springframework.stereotype.Service;import java.time.LocalDateTime;import java.util.List;
@Service public class AlertService {
 private final AlertRepository repo; public AlertService(AlertRepository repo){this.repo=repo;}
 private AlertDto map(Alert a){return new AlertDto(a.getId(),a.getRegion().getId(),a.getRegion().getName(),a.getTitle(),a.getDescription(),a.getSeverity(),a.getStatus(),a.getCreatedAt(),a.getResolvedAt());}
 public List<AlertDto> list(){return repo.findAll().stream().map(this::map).toList();}
 public List<AlertDto> active(){return repo.findByStatusIn(List.of(AlertStatus.OPEN,AlertStatus.MONITORING)).stream().map(this::map).toList();}
 public AlertDto resolve(Long id){Alert a=repo.findById(id).orElseThrow(()->new NotFoundException("Alerta não encontrado")); a.setStatus(AlertStatus.RESOLVED); a.setResolvedAt(LocalDateTime.now()); return map(repo.save(a));}
 public void createFromReading(Sensor sensor, Double value){
  Alert alert=null;
  if(sensor.getType()==SensorType.WATER_LEVEL && value>=80) alert=mk(sensor,"Risco de enchente","Nível de água acima do limite.",RiskLevel.HIGH);
  if(sensor.getType()==SensorType.TEMPERATURE && value>=40) alert=mk(sensor,"Risco de incêndio florestal","Temperatura extrema detectada.",RiskLevel.CRITICAL);
  if(sensor.getType()==SensorType.SMOKE && value>=70) alert=mk(sensor,"Alerta de fumaça","Concentração de fumaça elevada.",RiskLevel.CRITICAL);
  if(sensor.getType()==SensorType.RAINFALL && value>=60) alert=mk(sensor,"Alerta de chuva intensa","Volume de chuva elevado.",RiskLevel.HIGH);
  if(alert!=null) repo.save(alert);
 }
 private Alert mk(Sensor sensor, String t, String d, RiskLevel sev){Alert a=new Alert(); a.setRegion(sensor.getRegion()); a.setTitle(t); a.setDescription(d); a.setSeverity(sev); a.setStatus(AlertStatus.OPEN); return a;}
}
