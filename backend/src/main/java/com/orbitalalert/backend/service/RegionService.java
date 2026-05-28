package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.RegionDto;import com.orbitalalert.backend.entity.Region;import com.orbitalalert.backend.exception.NotFoundException;import com.orbitalalert.backend.repository.RegionRepository;import org.springframework.stereotype.Service;import java.util.List;
@Service public class RegionService {
 private final RegionRepository repo; public RegionService(RegionRepository repo){this.repo=repo;}
 private RegionDto map(Region r){return new RegionDto(r.getId(),r.getName(),r.getCity(),r.getState(),r.getLatitude(),r.getLongitude(),r.getSatelliteRiskScore(),r.getRiskLevel());}
 private void fill(Region r, RegionDto d){r.setName(d.name());r.setCity(d.city());r.setState(d.state());r.setLatitude(d.latitude());r.setLongitude(d.longitude());r.setSatelliteRiskScore(d.satelliteRiskScore());r.setRiskLevel(d.riskLevel());}
 public List<RegionDto> list(){return repo.findAll().stream().map(this::map).toList();}
 public RegionDto get(Long id){return map(repo.findById(id).orElseThrow(()->new NotFoundException("Região não encontrada")));}
 public RegionDto create(RegionDto d){Region r=new Region();fill(r,d);return map(repo.save(r));}
 public RegionDto update(Long id, RegionDto d){Region r=repo.findById(id).orElseThrow(()->new NotFoundException("Região não encontrada"));fill(r,d);return map(repo.save(r));}
 public void delete(Long id){if(!repo.existsById(id)) throw new NotFoundException("Região não encontrada"); repo.deleteById(id);} }
