# Low-Level Design (LLD) - Vehicle Telemetry Visualization MVP
## With UML Diagrams

**Document Version:** 1.0  
**Date:** 2026-10-05  
**Status:** MVP/POC  

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Component Diagrams](#component-diagrams)
3. [Data Model & ERD](#data-model--erd)
4. [Class Diagrams](#class-diagrams)
5. [Sequence Diagrams](#sequence-diagrams)
6. [State Diagrams](#state-diagrams)
7. [Module Breakdown](#module-breakdown)
8. [API Contract Details](#api-contract-details)
9. [Database Schema](#database-schema)
10. [Error Handling & Exceptions](#error-handling--exceptions)

---

## 1. System Architecture Overview

### 3-Tier Architecture

\`\`\`mermaid
graph TB
    User["👤 User<br/>Browser"]
    Dashboard["Streamlit Dashboard<br/>src/dashboard/"]
    APILayer["FastAPI Layer<br/>src/api/"]
    DataLayer["Data Layer<br/>src/telemetry/"]
    Database["SQLite Database<br/>data/telemetry.db"]
    
    User -->|HTTP/WebSocket| Dashboard
    Dashboard -->|REST API<br/>GET/POST| APILayer
    APILayer -->|Query/Write| DataLayer
    DataLayer -->|SQL| Database
    
    style User fill:#e1f5ff
    style Dashboard fill:#fff3e0
    style APILayer fill:#f3e5f5
    style DataLayer fill:#e8f5e9
    style Database fill:#fce4ec
\`\`\`

---

## 2. Component Architecture

\`\`\`mermaid
graph LR
    subgraph Client["Client Layer"]
        StreamlitApp["Streamlit<br/>Dashboard"]
    end
    
    subgraph API["API Layer"]
        FastAPIApp["FastAPI<br/>Application"]
        RouteHandler["Route<br/>Handlers"]
        SchemaValidator["Pydantic<br/>Schemas"]
        ErrorHandler["Exception<br/>Handler"]
    end
    
    subgraph Business["Business Logic"]
        QueryModule["Query<br/>Module"]
        AnomalyDetector["Anomaly<br/>Detector"]
        DataGenerator["Data<br/>Generator"]
    end
    
    subgraph Persistence["Data Layer"]
        SQLAlchemy["SQLAlchemy<br/>ORM"]
        DatabaseConn["Database<br/>Connection"]
    end
    
    subgraph Storage["Storage"]
        SQLiteDB["SQLite<br/>Database"]
    end
    
    StreamlitApp -->|API Calls| FastAPIApp
    FastAPIApp --> RouteHandler
    RouteHandler --> SchemaValidator
    RouteHandler --> ErrorHandler
    RouteHandler --> QueryModule
    QueryModule --> AnomalyDetector
    QueryModule --> SQLAlchemy
    SQLAlchemy --> DatabaseConn
    DatabaseConn --> SQLiteDB
    DataGenerator --> SQLiteDB
\`\`\`

---

## 3. Data Model & Entity Relationship Diagram

\`\`\`mermaid
erDiagram
    TELEMETRY ||--o{ ALERT : generates
    TELEMETRY ||--o{ ANOMALY_LOG : creates
    
    TELEMETRY {
        int id PK
        string vehicle_id FK
        datetime timestamp
        float speed_kmh
        float engine_temp_celsius
        float fuel_level_percent
        int rpm
        float acceleration_mps2
        string engine_status
        float battery_voltage
        boolean is_anomaly
        datetime created_at
    }
    
    ALERT {
        int id PK
        int telemetry_id FK
        string alert_type
        string severity
        string message
        datetime triggered_at
    }
    
    ANOMALY_LOG {
        int id PK
        int telemetry_id FK
        string anomaly_reason
        datetime detected_at
    }
\`\`\`

---

## 4. API Layer Class Diagram

\`\`\`mermaid
classDiagram
    class FastAPIApp {
        -str title
        -str version
        -List routers
        +setup_routes()
        +setup_middleware()
        +setup_exception_handlers()
    }
    
    class TelemetryRouter {
        +get_latest_telemetry()
        +get_telemetry_history()
        +export_telemetry_csv()
        +get_vehicles()
    }
    
    class TelemetrySchema {
        -str vehicle_id
        -datetime timestamp
        -float speed_kmh
        -float engine_temp_celsius
        -float fuel_level_percent
        -int rpm
        +dict()
    }
    
    class TelemetryQueryService {
        -SessionLocal db
        +get_latest()
        +get_history()
        +get_all_vehicles()
        +export_csv()
    }
    
    class APIException {
        -int status_code
        -str detail
    }
    
    FastAPIApp --> TelemetryRouter: contains
    TelemetryRouter --> TelemetrySchema: uses
    TelemetryRouter --> TelemetryQueryService: calls
    TelemetryRouter --> APIException: raises
\`\`\`

---

## 5. Dashboard Layer Class Diagram

\`\`\`mermaid
classDiagram
    class StreamlitApp {
        +render_page()
        +setup_session_state()
        +load_css()
    }
    
    class APIClient {
        -str base_url
        -aiohttp.ClientSession session
        +get_latest_telemetry()
        +get_telemetry_history()
        +export_telemetry()
        +health_check()
    }
    
    class GaugeComponent {
        -float value
        -str unit
        -float min_val
        -float max_val
        +render()
        +get_color_for_value()
    }
    
    class ChartComponent {
        -List data_points
        -str chart_type
        -str title
        +render()
        +prepare_data()
    }
    
    class AlertPanel {
        -List alerts
        +render()
        +filter_by_severity()
    }
    
    StreamlitApp --> APIClient: calls
    StreamlitApp --> GaugeComponent: uses
    StreamlitApp --> ChartComponent: uses
    StreamlitApp --> AlertPanel: displays
\`\`\`

---

## 6. Business Logic Layer Class Diagram

\`\`\`mermaid
classDiagram
    class AnomalyDetector {
        +detect_overheat()$ bool
        +detect_low_fuel()$ bool
        +detect_high_rpm()$ bool
        +detect_extreme_acceleration()$ bool
        +check_all_rules()$ List
    }
    
    class DataGenerator {
        -int record_count
        -int hours_back
        +generate_realistic_values()
        +insert_to_db()
        +add_anomalies()
    }
    
    class ExportService {
        +to_csv()$ bool
        +to_json()$ str
        +format_timestamp()$ str
    }
    
    class CacheManager {
        -Dict cache_storage
        -int ttl_seconds
        +get()$ Any
        +set()
        +invalidate()
    }
\`\`\`

---

## 7. Data Access Sequence Diagram - Get Latest Telemetry

\`\`\`mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant APIClient
    participant FastAPI
    participant TelemetryService
    participant Database
    
    User->>Streamlit: Open http://localhost:8501
    Streamlit->>APIClient: Initialize client
    APIClient->>FastAPI: GET /api/telemetry/latest
    FastAPI->>TelemetryService: get_latest(vehicle_id)
    TelemetryService->>Database: SELECT * FROM telemetry DESC LIMIT 1
    Database-->>TelemetryService: Telemetry record
    TelemetryService-->>FastAPI: TelemetrySchema JSON
    FastAPI-->>APIClient: 200 OK + JSON
    APIClient-->>Streamlit: Latest telemetry data
    Streamlit->>Streamlit: Render gauges
    Streamlit-->>User: Dashboard displayed
\`\`\`

---

## 8. Historical Data Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant APIClient
    participant FastAPI
    participant CacheManager
    participant TelemetryService
    participant Database
    
    User->>Streamlit: Select date range (24h)
    Streamlit->>APIClient: get_telemetry_history()
    APIClient->>FastAPI: GET /api/telemetry/history?hours=24
    FastAPI->>CacheManager: Check cache
    alt Cache Hit
        CacheManager-->>FastAPI: Cached data
    else Cache Miss
        FastAPI->>TelemetryService: get_history()
        TelemetryService->>Database: SELECT * WHERE timestamp > ?
        Database-->>TelemetryService: List[Telemetry]
        TelemetryService->>CacheManager: Store in cache (300s)
        TelemetryService-->>FastAPI: List[TelemetrySchema]
    end
    FastAPI-->>APIClient: 200 OK + List
    APIClient-->>Streamlit: Historical data
    Streamlit->>Streamlit: Render charts
    Streamlit-->>User: Charts displayed
\`\`\`

---

## 9. Real-Time Update Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant Streamlit
    participant SessionState
    participant Timer
    participant APIClient
    participant FastAPI
    participant Database
    
    Streamlit->>SessionState: Initialize last_update
    loop Every 2 seconds
        Timer->>Streamlit: Trigger rerun
        Streamlit->>APIClient: get_latest_telemetry()
        APIClient->>FastAPI: GET /api/telemetry/latest
        FastAPI->>Database: Get latest record
        Database-->>FastAPI: Telemetry record
        FastAPI-->>APIClient: JSON response
        APIClient-->>Streamlit: Updated data
        Streamlit->>Streamlit: Update gauges
        Streamlit->>SessionState: Update timestamp
    end
\`\`\`

---

## 10. CSV Export Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant APIClient
    participant FastAPI
    participant ExportService
    participant Database
    
    User->>Streamlit: Click "Export to CSV"
    Streamlit->>Streamlit: Show date range selector
    User->>Streamlit: Confirm export
    Streamlit->>APIClient: export_telemetry()
    APIClient->>FastAPI: GET /api/telemetry/export?vehicle_id=V001
    FastAPI->>ExportService: generate_csv()
    ExportService->>Database: SELECT * WHERE vehicle_id=? AND timestamp BETWEEN ?
    Database-->>ExportService: List[Telemetry]
    ExportService->>ExportService: Format CSV with headers
    ExportService-->>FastAPI: FileResponse
    FastAPI-->>APIClient: CSV stream
    APIClient-->>Streamlit: Binary data
    Streamlit-->>User: Download telemetry_export.csv
\`\`\`

---

## 11. Anomaly Detection Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant API
    participant AnomalyDetector
    participant RuleEngine
    participant Database
    participant AlertService
    
    API->>AnomalyDetector: check_all_rules(telemetry)
    AnomalyDetector->>RuleEngine: detect_overheat(temp)
    RuleEngine-->>AnomalyDetector: bool
    AnomalyDetector->>RuleEngine: detect_low_fuel(fuel)
    RuleEngine-->>AnomalyDetector: bool
    AnomalyDetector->>RuleEngine: detect_high_rpm(rpm)
    RuleEngine-->>AnomalyDetector: bool
    AnomalyDetector->>RuleEngine: detect_extreme_accel(accel)
    RuleEngine-->>AnomalyDetector: bool
    alt Any anomaly detected
        AnomalyDetector->>AlertService: create_alerts()
        AlertService->>Database: INSERT INTO alerts
        AlertService->>Database: UPDATE telemetry SET is_anomaly=TRUE
    end
\`\`\`

---

## 12. Dashboard State Machine

\`\`\`mermaid
stateDiagram-v2
    [*] --> Initializing
    
    Initializing --> Loading: Session created
    Loading --> ConnectingAPI: Fetch config
    ConnectingAPI --> APIHealthCheck: Connect
    APIHealthCheck --> FetchingLatest: API healthy
    APIHealthCheck --> ErrorState: API unreachable
    
    FetchingLatest --> RenderDashboard: Data received
    FetchingLatest --> ErrorState: Fetch failed
    
    RenderDashboard --> Monitoring: Display complete
    Monitoring --> RefreshCycle: Auto-refresh (2s)
    RefreshCycle --> FetchingLatest: Poll API
    
    Monitoring --> UserAction: User interaction
    UserAction --> Monitoring: Action complete
    
    ErrorState --> Retry: Retry
    Retry --> ConnectingAPI
    
    Monitoring --> [*]: Close
\`\`\`

---

## 13. Data Lifecycle State Machine

\`\`\`mermaid
stateDiagram-v2
    [*] --> Generated
    
    Generated --> ValidatingSchema: Create
    ValidatingSchema --> Validated: Valid
    ValidatingSchema --> Invalid: Invalid
    Invalid --> [*]
    
    Validated --> CheckingAnomalies: Check rules
    CheckingAnomalies --> Normal: No anomaly
    CheckingAnomalies --> Anomalous: Anomaly detected
    
    Normal --> Stored: Insert DB
    Anomalous --> CreatingAlerts: Create alerts
    CreatingAlerts --> Stored: Insert DB
    
    Stored --> Queryable: Available
    Queryable --> Cached: Cache 300s
    Cached --> Expired: TTL expired
    Expired --> Queryable
    
    Queryable --> Archived: 7+ days old
    Archived --> [*]
\`\`\`

---

## 14. Module Directory Structure

### Phase 1: Data Layer
\`\`\`
src/telemetry/
├── __init__.py
├── models.py                  # SQLAlchemy ORM
├── database.py                # DB connection & session
├── config.py                  # Configuration
└── data_generator.py          # Sample data
\`\`\`

### Phase 2: API Layer
\`\`\`
src/api/
├── __init__.py
├── main.py                    # FastAPI app
├── routes/
│   └── telemetry.py          # Endpoints
├── schemas.py                 # Pydantic models
├── exceptions.py              # Custom exceptions
└── middleware/
    ├── error_handler.py
    └── logging.py
\`\`\`

### Phase 3: Dashboard
\`\`\`
src/dashboard/
├── __init__.py
├── app.py                     # Main Streamlit app
├── api_client.py              # API communication
├── gauges.py                  # Gauge components
├── charts.py                  # Chart components
├── status_panel.py            # Status indicators
└── .streamlit/
    └── config.toml
\`\`\`

### Phase 4: Streaming & Integration
\`\`\`
src/dashboard/
├── streaming.py               # Real-time updates
└── export.py                  # CSV export

src/telemetry/
├── anomaly_detector.py        # Enhanced
└── data_retention.py          # Cleanup
\`\`\`

---

## 15. API Endpoint Specifications

### GET /api/telemetry/latest
**Request:**
- Query Parameters: vehicle_id (optional)

**Response (200 OK):**
\`\`\`json
{
  "vehicle_id": "VEHICLE_001",
  "timestamp": "2026-10-05T10:30:45Z",
  "speed_kmh": 65.5,
  "engine_temp_celsius": 85.2,
  "fuel_level_percent": 75,
  "rpm": 2500,
  "acceleration_mps2": 0.5,
  "engine_status": "running",
  "battery_voltage": 12.8,
  "warnings": []
}
\`\`\`

### GET /api/telemetry/history
**Request:**
- Query Parameters: vehicle_id (required), hours (optional, default=24), limit (optional, default=100)

**Response (200 OK):**
\`\`\`json
[
  {
    "timestamp": "2026-10-05T10:29:45Z",
    "speed_kmh": 65.0,
    "engine_temp_celsius": 85.0,
    "fuel_level_percent": 75.2,
    "rpm": 2480,
    "acceleration_mps2": 0.3
  }
]
\`\`\`

### GET /api/telemetry/export
**Request:**
- Query Parameters: vehicle_id (required), start_date (optional), end_date (optional), format (default=csv)

**Response (200 OK):**
- Content-Type: text/csv
- Binary CSV stream with headers

### GET /health
**Response (200 OK):**
\`\`\`json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-10-05T10:30:45Z"
}
\`\`\`

---

## 16. Database Schema

\`\`\`sql
-- Telemetry table
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    speed_kmh REAL NOT NULL,
    engine_temp_celsius REAL NOT NULL,
    fuel_level_percent REAL NOT NULL,
    rpm INTEGER NOT NULL,
    acceleration_mps2 REAL NOT NULL,
    engine_status VARCHAR(20) NOT NULL,
    battery_voltage REAL NOT NULL,
    is_anomaly BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vehicle_timestamp ON telemetry(vehicle_id, timestamp DESC);
CREATE INDEX idx_timestamp ON telemetry(timestamp DESC);
CREATE INDEX idx_anomaly ON telemetry(is_anomaly);

-- Alerts table
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telemetry_id INTEGER NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message VARCHAR(255),
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(telemetry_id) REFERENCES telemetry(id)
);

CREATE INDEX idx_alerts_telemetry ON alerts(telemetry_id);
\`\`\`

---

## 17. Error Handling Hierarchy

\`\`\`mermaid
classDiagram
    class APIException {
        -int status_code
        -str detail
    }
    
    class VehicleNotFoundError {
        -int status_code = 404
    }
    
    class InvalidDateRangeError {
        -int status_code = 400
    }
    
    class DatabaseConnectionError {
        -int status_code = 503
    }
    
    class ExportError {
        -int status_code = 500
    }
    
    APIException <|-- VehicleNotFoundError
    APIException <|-- InvalidDateRangeError
    APIException <|-- DatabaseConnectionError
    APIException <|-- ExportError
\`\`\`

---

## 18. Anomaly Detection Rules

| Rule | Threshold | Duration | Alert Type | Severity |
|------|-----------|----------|-----------|----------|
| Overheat | Temp > 100°C | Immediate | Critical | Red |
| Low Fuel | Fuel < 15% | Immediate | Warning | Yellow |
| High RPM | RPM > 6000 | > 5 minutes | Warning | Yellow |
| Extreme Acceleration | Accel > 5 m/s² | > 3 seconds | Warning | Yellow |

---

## 19. Performance & Optimization Guidelines

- **Database Indexes:** vehicle_id + timestamp for fast queries
- **Query Limits:** Max 1000 records per request
- **Cache TTL:** 300 seconds for history queries
- **API Response Time:** < 500ms target
- **Dashboard Refresh:** 2 seconds (configurable)
- **Batch Inserts:** Group anomaly data writes

---

## 20. Testing Coverage Targets

| Phase | Unit | Integration | Manual | Overall |
|-------|------|-------------|--------|---------|
| 1 | 85% | 70% | - | 80% |
| 2 | 85% | 80% | - | 82% |
| 3 | 75% | 80% | 90% | 80% |
| 4 | 85% | 90% | 95% | 85%+ |

---

**End of Low-Level Design Document**