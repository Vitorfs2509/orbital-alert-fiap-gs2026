package com.orbitalalert.backend.repository;
import com.orbitalalert.backend.entity.Alert;import com.orbitalalert.backend.entity.AlertStatus;import org.springframework.data.jpa.repository.JpaRepository;import java.util.List;
public interface AlertRepository extends JpaRepository<Alert,Long>{ List<Alert> findByStatusIn(List<AlertStatus> statuses); }
