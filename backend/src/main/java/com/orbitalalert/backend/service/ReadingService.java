package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.RawEventDto;import com.orbitalalert.backend.dto.ReadingDto.*;import com.orbitalalert.backend.entity.Sensor;import com.orbitalalert.backend.entity.SensorReading;import com.orbitalalert.backend.exception.NotFoundException;import com.orbitalalert.backend.repository.SensorReadingRepository;import com.orbitalalert.backend.repository.SensorRepository;import org.springframework.stereotype.Service;import java.time.LocalDateTime;import java.util.List;import java.util.UUID;
@Service public class ReadingService {
 private final SensorReadingRepository repo; private final SensorRepository sensorRepo; private final AlertService alertService; private final DataLakeService dataLake;
 public ReadingService(SensorReadingRepository repo, SensorRepository sensorRepo, AlertService alertService, DataLakeService dataLake){this.repo=repo;this.sensorRepo=sensorRepo;this.alertService=alertService;this.dataLake=dataLake;}
 private ReadingResponse map(SensorReading r){return new ReadingResponse(r.getId(),r.getSensor().getId(),r.getSensor().getType().name(),r.getValue(),r.getMeasuredAt());}
 public ReadingResponse create(CreateReadingRequest req){
  Sensor s=sensorRepo.findById(req.sensorId()).orElseThrow(()->new NotFoundException("Sensor não encontrado"));
  LocalDateTime now=LocalDateTime.now(java.time.ZoneOffset.UTC);
  SensorReading sr=new SensorReading(); sr.setSensor(s); sr.setValue(req.value()); sr.setMeasuredAt(now); sr=repo.save(sr);
  alertService.createFromReading(s, req.value());
  // Falha de escrita do RAW nao desfaz a leitura nem o alerta no banco operacional.
  dataLake.writeRawEvent(new RawEventDto(UUID.randomUUID().toString(), s.getId(), s.getRegion().getId(),
    s.getType().name(), req.value(), s.getUnit(), sr.getMeasuredAt(), now,
    req.source()==null||req.source().isBlank()?"API":req.source(), sr.getId()));
  return map(sr);
 }
 public List<ReadingResponse> latest(){return repo.findLatestPerSensor().stream().map(this::map).toList();}
}
