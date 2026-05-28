package com.orbitalalert.backend.dto;

import com.orbitalalert.backend.entity.UserRole;
import jakarta.validation.constraints.*;

public class AuthDtos {
    public record RegisterRequest(@NotBlank String name, @Email @NotBlank String email, @NotBlank @Size(min = 6) String password, @NotNull UserRole role) {}
    public record LoginRequest(@Email @NotBlank String email, @NotBlank String password) {}
    public record AuthResponse(Long id, String name, String email, UserRole role) {}
}
