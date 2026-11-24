package com.orbitalalert.backend;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = {"ORBITAL_ADMIN_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "ORBITAL_INGEST_TOKEN=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"})
@AutoConfigureMockMvc
class ApiSecurityTests {
    private static final String ADMIN = "Bearer " + "a".repeat(32);
    private static final String SENSOR = "Bearer " + "b".repeat(32);

    @Autowired MockMvc mvc;

    @Test
    void publicDashboardReadsAndPrivateDiagnosticsFollowPolicy() throws Exception {
        mvc.perform(get("/api/regions")).andExpect(status().isOk());
        mvc.perform(get("/api/health")).andExpect(status().isOk());
        mvc.perform(get("/api/recommendations/regions/1/prompt")).andExpect(status().isUnauthorized());
    }

    @Test
    void ingestionRequiresItsOwnCredential() throws Exception {
        String payload = "{\"sensorId\":999999,\"value\":95}";
        mvc.perform(post("/api/readings").contentType("application/json").content(payload))
                .andExpect(status().isUnauthorized());
        mvc.perform(post("/api/readings").header("Authorization", "Bearer invalid")
                .contentType("application/json").content(payload)).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/readings").header("Authorization", ADMIN)
                .contentType("application/json").content(payload)).andExpect(status().isForbidden());
        mvc.perform(post("/api/readings").header("Authorization", SENSOR)
                .contentType("application/json").content(payload)).andExpect(status().isNotFound());
    }

    @Test
    void administrativeChangesRejectAnonymousAndIngestionUsers() throws Exception {
        mvc.perform(put("/api/alerts/999999/resolve")).andExpect(status().isUnauthorized());
        mvc.perform(put("/api/alerts/999999/resolve").header("Authorization", SENSOR))
                .andExpect(status().isForbidden());
        mvc.perform(put("/api/alerts/999999/resolve").header("Authorization", ADMIN))
                .andExpect(status().isNotFound());
        mvc.perform(post("/api/auth/register")).andExpect(status().isUnauthorized());
    }
}
