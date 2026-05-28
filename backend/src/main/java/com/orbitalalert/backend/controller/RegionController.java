package com.orbitalalert.backend.controller;
import com.orbitalalert.backend.dto.RegionDto;import com.orbitalalert.backend.service.RegionService;import jakarta.validation.Valid;import org.springframework.web.bind.annotation.*;import java.util.List;
@RestController @RequestMapping("/api/regions")
public class RegionController { private final RegionService service; public RegionController(RegionService service){this.service=service;}
 @GetMapping public List<RegionDto> list(){return service.list();}
 @GetMapping("/{id}") public RegionDto get(@PathVariable Long id){return service.get(id);} 
 @PostMapping public RegionDto create(@RequestBody @Valid RegionDto dto){return service.create(dto);} 
 @PutMapping("/{id}") public RegionDto update(@PathVariable Long id,@RequestBody @Valid RegionDto dto){return service.update(id,dto);} 
 @DeleteMapping("/{id}") public void delete(@PathVariable Long id){service.delete(id);} }
