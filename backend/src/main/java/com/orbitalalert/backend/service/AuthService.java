package com.orbitalalert.backend.service;
import com.orbitalalert.backend.dto.AuthDtos.*;import com.orbitalalert.backend.entity.User;import com.orbitalalert.backend.exception.BadRequestException;import com.orbitalalert.backend.repository.UserRepository;import org.springframework.security.crypto.password.PasswordEncoder;import org.springframework.stereotype.Service;
@Service
public class AuthService {
 private final UserRepository repo; private final PasswordEncoder encoder;
 public AuthService(UserRepository repo, PasswordEncoder encoder){this.repo=repo;this.encoder=encoder;}
 public AuthResponse register(RegisterRequest r){ if(repo.existsByEmail(r.email())) throw new BadRequestException("E-mail já cadastrado"); User u=new User(); u.setName(r.name());u.setEmail(r.email());u.setPasswordHash(encoder.encode(r.password()));u.setRole(r.role()); repo.save(u); return new AuthResponse(u.getId(),u.getName(),u.getEmail(),u.getRole()); }
 public AuthResponse login(LoginRequest r){ User u=repo.findByEmail(r.email()).orElseThrow(()->new BadRequestException("Credenciais inválidas")); if(!encoder.matches(r.password(),u.getPasswordHash())) throw new BadRequestException("Credenciais inválidas"); return new AuthResponse(u.getId(),u.getName(),u.getEmail(),u.getRole()); }
}
