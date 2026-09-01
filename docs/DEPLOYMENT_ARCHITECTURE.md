# Deployment & Infrastructure Architecture Specification
## Containerization, CI/CD Pipeline & Production Topology

**Document Version:** 1.0.0  
**Container Engine:** Docker / Multi-Stage OpenJDK 21 Runtime  
**Orchestration (V1):** Docker Compose / Managed Container Service (ECS / Cloud Run / VPS)  
**CI/CD Engine:** GitHub Actions  
**Date:** September 2026  

---

## 1. Production Deployment Topology

```text
                                  Internet
                                     │
                             [ Cloudflare CDN & WAF ]
                                     │ HTTPS (TLS 1.3)
                                     ▼
                             [ Nginx Reverse Proxy ]
                                     │
                      ┌──────────────┴──────────────┐
                      │ Load Balancing (Round Robin)│
                      ▼                             ▼
         ┌────────────────────────┐    ┌────────────────────────┐
         │ Spring Boot Instance 1 │    │ Spring Boot Instance 2 │
         │   (Docker - Java 21)   │    │   (Docker - Java 21)   │
         └───────────┬────────────┘    └───────────┬────────────┘
                     │                             │
                     └──────────────┬──────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ PostgreSQL 16    │    │ Redis 7.2        │    │ RabbitMQ 3.13    │
  │ Primary DB + WAL │    │ Cache & Redlock  │    │ Async Broker     │
  └──────────────────┘    └──────────────────┘    └──────────────────┘
```

> **Note on Microservices / Kubernetes:** In alignment with our V1 modular monolith decision, **Kubernetes and Service Mesh are intentionally avoided for initial deployment** to reduce infrastructure costs and operational complexity. Standard container-based deployment delivers high availability at $<20\%$ of Kubernetes management cost.

---

## 2. Multi-Stage Docker Build (`backend/Dockerfile`)

```dockerfile
# Stage 1: Build & Package
FROM maven:3.9-eclipse-temurin-21-alpine AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Minimal Distroless / Alpine Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseZGC", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
```

---

## 3. Continuous Integration & Continuous Deployment (CI/CD)

```text
[ Developer Pushes Code / Opens PR ]
                  │
                  ▼
         [ GitHub Actions CI ]
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│ Backend CI    │   │ Frontend CI   │
│ • JDK 21 Setup│   │ • Node 20     │
│ • Flyway Check│   │ • ESLint      │
│ • Testcontain.│   │ • Vitest / RTL│
│ • Maven Build │   │ • Vite Build  │
└───────┬───────┘   └───────┬───────┘
        └─────────┬─────────┘
                  │ (Merge to 'main')
                  ▼
       [ Build Docker Images ]
                  │
                  ▼
    [ Deploy to Production Server ]
                  │
                  ▼
       [ Run Flyway Migrations ]
                  │
                  ▼
    [ Rolling Container Restart ]
```

---

*Governed by Twelve-Factor App principles and automated DevSecOps standards.*
