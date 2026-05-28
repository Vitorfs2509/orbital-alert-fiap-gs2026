package com.orbitalalert.backend.controller;
import com.orbitalalert.backend.dto.ReadingDto.*;import com.orbitalalert.backend.service.ReadingService;import jakarta.validation.Valid;import org.springframework.web.bind.annotation.*;import java.util.List;
@RestController @RequestMapping("/api/readings")
public class ReadingController { private final ReadingService service; public ReadingController(ReadingService service){this.service=service;}
 @PostMapping public ReadingResponse create(@RequestBody @Valid CreateReadingRequest req){return service.create(req);} 
 @GetMapping("/latest") public List<ReadingResponse> latest(){return service.latest();} }
