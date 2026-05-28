package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.SensorDto;import com.orbitalalert.backend.entity.Sensor;import com.orbitalalert.backend.exception.NotFoundException;import com.orbitalalert.backend.repository.RegionRepository;import com.orbitalalert.backend.repository.SensorRepository;import org.springframework.stereotype.Service;import java.util.List;
@Service public class SensorService {
 private final SensorRepository sensorRepo; private final RegionRepository regionRepo;
 public SensorService(SensorRepository sensorRepo, RegionRepository regionRepo){this.sensorRepo=sensorRepo;this.regionRepo=regionRepo;}
 private SensorDto map(Sensor s){return new SensorDto(s.getId(),s.getRegion().getId(),s.getType(),s.getStatus(),s.getUnit());}
 public List<SensorDto> list(){return sensorRepo.findAll().stream().map(this::map).toList();}
 public SensorDto get(Long id){return map(sensorRepo.findById(id).orElseThrow(()->new NotFoundException("Sensor não encontrado")));}
 public SensorDto create(SensorDto d){Sensor s=new Sensor(); s.setRegion(regionRepo.findById(d.regionId()).orElseThrow(()->new NotFoundException("Região não encontrada"))); s.setType(d.type()); s.setStatus(d.status()); s.setUnit(d.unit()); return map(sensorRepo.save(s));}
 public void delete(Long id){if(!sensorRepo.existsById(id)) throw new NotFoundException("Sensor não encontrado"); sensorRepo.deleteById(id);} }
