package com.orbitalalert.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.AnonymousAuthenticationFilter;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

@Configuration
public class SecurityConfig {
    @Bean
    PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    SecurityFilterChain securityFilterChain(
            HttpSecurity http,
            @Value("${ORBITAL_ADMIN_TOKEN:}") String adminToken,
            @Value("${ORBITAL_INGEST_TOKEN:}") String ingestToken) throws Exception {
        if (!adminToken.isEmpty() && adminToken.equals(ingestToken)) {
            throw new IllegalArgumentException("Use credenciais diferentes para administração e ingestão");
        }
        return http
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                // Only explicit Bearer headers authorize writes. No browser cookies or HTTP Basic.
                .csrf(csrf -> csrf.disable())
                .exceptionHandling(errors -> errors.authenticationEntryPoint(new HttpStatusEntryPoint(HttpStatus.UNAUTHORIZED)))
                .addFilterBefore(new ServiceTokens(adminToken, ingestToken), AnonymousAuthenticationFilter.class)
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.GET, "/api/health", "/api/regions", "/api/regions/*",
                                "/api/sensors", "/api/sensors/*", "/api/readings/latest", "/api/alerts",
                                "/api/alerts/active", "/api/risk", "/api/recommendations/regions/*").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/readings").hasRole("INGEST")
                        .requestMatchers("/api/auth/register", "/api/regions/**", "/api/sensors/**",
                                "/api/alerts/**", "/api/recommendations/**",
                                "/swagger-ui.html", "/swagger-ui/**", "/v3/api-docs/**").hasRole("ADMIN")
                        .anyRequest().denyAll())
                .build();
    }

    private static final class ServiceTokens extends OncePerRequestFilter {
        private final String adminToken;
        private final String ingestToken;

        private ServiceTokens(String adminToken, String ingestToken) {
            this.adminToken = adminToken;
            this.ingestToken = ingestToken;
        }

        @Override
        protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
                throws IOException, ServletException {
            String header = request.getHeader("Authorization");
            if (header != null && header.startsWith("Bearer ")) {
                String supplied = header.substring(7);
                if (matches(adminToken, supplied)) {
                    authenticate("orbital-admin", "ADMIN");
                } else if (matches(ingestToken, supplied)) {
                    authenticate("orbital-sensor", "INGEST");
                }
            }
            chain.doFilter(request, response);
        }

        private static boolean matches(String expected, String supplied) {
            return expected.length() >= 32 && MessageDigest.isEqual(expected.getBytes(StandardCharsets.UTF_8),
                    supplied.getBytes(StandardCharsets.UTF_8));
        }

        private static void authenticate(String principal, String role) {
            var authentication = UsernamePasswordAuthenticationToken.authenticated(principal, null,
                    List.of(new SimpleGrantedAuthority("ROLE_" + role)));
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }
    }
}
