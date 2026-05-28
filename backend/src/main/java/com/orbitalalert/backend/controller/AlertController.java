package com.orbitalalert.backend.controller;
import com.orbitalalert.backend.dto.AlertDto;import com.orbitalalert.backend.service.AlertService;import org.springframework.web.bind.annotation.*;import java.util.List;
@RestController @RequestMapping("/api/alerts")
public class AlertController { private final AlertService service; public AlertController(AlertService service){this.service=service;}
 @GetMapping public List<AlertDto> list(){return service.list();}
 @GetMapping("/active") public List<AlertDto> active(){return service.active();}
 @PutMapping("/{id}/resolve") public AlertDto resolve(@PathVariable Long id){return service.resolve(id);} }
