package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.ReadingDto.*;import com.orbitalalert.backend.entity.Sensor;import com.orbitalalert.backend.entity.SensorReading;import com.orbitalalert.backend.exception.NotFoundException;import com.orbitalalert.backend.repository.SensorReadingRepository;import com.orbitalalert.backend.repository.SensorRepository;import org.springframework.stereotype.Service;import java.time.LocalDateTime;import java.util.List;
@Service public class ReadingService {
 private final SensorReadingRepository repo; private final SensorRepository sensorRepo; private final AlertService alertService;
 public ReadingService(SensorReadingRepository repo, SensorRepository sensorRepo, AlertService alertService){this.repo=repo;this.sensorRepo=sensorRepo;this.alertService=alertService;}
 private ReadingResponse map(SensorReading r){return new ReadingResponse(r.getId(),r.getSensor().getId(),r.getSensor().getType().name(),r.getValue(),r.getMeasuredAt());}
 public ReadingResponse create(CreateReadingRequest req){Sensor s=sensorRepo.findById(req.sensorId()).orElseThrow(()->new NotFoundException("Sensor não encontrado")); SensorReading sr=new SensorReading(); sr.setSensor(s); sr.setValue(req.value()); sr.setMeasuredAt(LocalDateTime.now()); sr=repo.save(sr); alertService.createFromReading(s, req.value()); return map(sr);} 
 public List<ReadingResponse> latest(){return repo.findLatestPerSensor().stream().map(this::map).toList();}
}
