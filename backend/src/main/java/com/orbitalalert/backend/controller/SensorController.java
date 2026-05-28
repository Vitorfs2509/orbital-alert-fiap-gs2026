package com.orbitalalert.backend.controller;
import com.orbitalalert.backend.dto.SensorDto;import com.orbitalalert.backend.service.SensorService;import jakarta.validation.Valid;import org.springframework.web.bind.annotation.*;import java.util.List;
@RestController @RequestMapping("/api/sensors")
public class SensorController { private final SensorService service; public SensorController(SensorService service){this.service=service;}
 @GetMapping public List<SensorDto> list(){return service.list();}
 @GetMapping("/{id}") public SensorDto get(@PathVariable Long id){return service.get(id);} 
 @PostMapping public SensorDto create(@RequestBody @Valid SensorDto dto){return service.create(dto);} 
 @DeleteMapping("/{id}") public void delete(@PathVariable Long id){service.delete(id);} }
