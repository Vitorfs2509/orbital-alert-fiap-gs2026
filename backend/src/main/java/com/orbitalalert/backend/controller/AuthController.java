package com.orbitalalert.backend.controller;
import com.orbitalalert.backend.dto.AuthDtos.*;import com.orbitalalert.backend.service.AuthService;import jakarta.validation.Valid;import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/auth")
public class AuthController {
 private final AuthService service; public AuthController(AuthService service){this.service=service;}
 @PostMapping("/register") public AuthResponse register(@RequestBody @Valid RegisterRequest req){return service.register(req);} 
 @PostMapping("/login") public AuthResponse login(@RequestBody @Valid LoginRequest req){return service.login(req);} }
