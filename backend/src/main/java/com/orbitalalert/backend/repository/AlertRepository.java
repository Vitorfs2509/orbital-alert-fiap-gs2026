package com.orbitalalert.backend.repository;

import com.orbitalalert.backend.entity.Alert;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AlertRepository extends JpaRepository<Alert, Long> {
}
