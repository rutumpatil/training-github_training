# Vehicle Telemetry Visualization - Technical Specification
## MVP/POC Version

**Document Version:** 1.0  
**Date:** 2026-10-05  
**Status:** MVP/POC  

---

## 1. Overview

This document outlines a lightweight visualization dashboard for real-time vehicle telemetry data. The MVP focuses on displaying core vehicle metrics from simulated sensor data without production-grade complexity.

### Scope
- Real-time telemetry data visualization
- Single vehicle dashboard
- Basic charts and gauges
- Simple data filtering by time range
- No user authentication or multi-tenancy

---

## 2. Objectives

1. Display real-time vehicle sensor data in an intuitive UI
2. Show historical trends for key metrics (last 24 hours)
3. Identify anomalies through basic visual indicators
4. Enable quick vehicle health assessment
5. Export data as CSV for analysis

---

## 3. Key Metrics to Visualize

### Real-time Gauges
- **Speed:** 0-200 km/h with warning zones
- **Engine Temperature:** 0-120°C with danger threshold
- **Fuel Level:** 0-100% with low fuel indicator
- **Engine RPM:** 0-8000 RPM

### Time-Series Charts
- **Speed Over Time:** Last 1 hour (line chart)
- **Temperature Trend:** Last 24 hours (area chart)
- **Fuel Consumption Rate:** Last 24 hours (bar chart)
- **Acceleration Profile:** Last 1 hour (scatter plot)

### Status Indicators
- **Engine Status:** Running/Off (green/red)
- **Battery Voltage:** Healthy/Warning/Critical
- **System Alerts:** Count of active warnings

---

## 4. Technical Architecture

### Frontend Stack
- **Framework:** Streamlit (Python-based web framework)
- **Visualization Library:** Plotly for interactive charts
- **UI Components:** Streamlit built-in widgets (gauges simulated via custom plots)
- **Data Refresh:** Auto-refresh every 2 seconds

### Backend Stack
- **API:** FastAPI (async endpoints)
- **Data Source:** SQLite (development) / PostgreSQL (ready for upgrade)
- **Data Format:** JSON REST API responses
- **Cache:** In-memory cache for latest values

### Data Flow
```
Sensor Data (Simulated)
    ↓
API Endpoint (/api/telemetry/latest)
    ↓
Streamlit Dashboard
    ↓
Plotly Charts + Gauges
```

---

## 5. Dashboard Layout

### Page Structure
```
┌─────────────────────────────────────────────────────┐
│  Vehicle Telemetry Dashboard - MVP                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Vehicle: [Dropdown] | Time Range: [Date Picker]  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  STATUS PANEL (Row 1)                              │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │ Speed    │ Temp     │ Fuel     │ RPM      │     │
│  │ (Gauge)  │ (Gauge)  │ (Gauge)  │ (Gauge)  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
│                                                     │
│  ALERTS (Row 2)                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │ Engine Status: RUNNING ✓                    │   │
│  │ Battery: 12.5V ✓                            │   │
│  │ Active Warnings: 0                          │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  CHARTS (Row 3 & 4)                               │
│  ┌─────────────────────┬─────────────────────┐    │
│  │ Speed Over Time     │ Temperature Trend   │    │
│  │                     │                     │    │
│  └─────────────────────┴─────────────────────┘    │
│  ┌─────────────────────┬─────────────────────┐    │
│  │ Fuel Consumption    │ Acceleration Log    │    │
│  │                     │                     │    │
│  └─────────────────────┴─────────────────────┘    │
│                                                     │
│  [Export to CSV] [Refresh Now]                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 6. API Endpoints (MVP)

### 1. Get Latest Telemetry
```
GET /api/telemetry/latest
Response:
{
  "vehicle_id": "VEHICLE_001",
  "timestamp": "2026-10-05T10:30:45Z",
  "speed_kmh": 65.5,
  "engine_temp_celsius": 85.2,
  "fuel_level_percent": 75,
  "rpm": 2500,
  "engine_status": "running",
  "battery_voltage": 12.8,
  "warnings": []
}
```

### 2. Get Historical Data
```
GET /api/telemetry/history?vehicle_id=VEHICLE_001&hours=24
Response:
[
  {
    "timestamp": "2026-10-05T10:29:45Z",
    "speed_kmh": 65.0,
    "engine_temp_celsius": 85.0,
    "fuel_level_percent": 75.2,
    "rpm": 2480
  },
  ...
]
```

### 3. Export Data
```
GET /api/telemetry/export?vehicle_id=VEHICLE_001&format=csv
Response: CSV file download
```

---

## 7. Data Model

### Telemetry Record
```python
{
  "id": int,
  "vehicle_id": str,
  "timestamp": datetime,
  "speed_kmh": float,
  "engine_temp_celsius": float,
  "fuel_level_percent": float,
  "rpm": int,
  "acceleration_mps2": float,
  "engine_status": str,  # "running" | "off"
  "battery_voltage": float,
  "is_anomaly": bool
}
```

---

## 8. Anomaly Detection (Simple)

### Alert Rules
1. **Overheat Alert:** Engine temp > 100°C
2. **Low Fuel Alert:** Fuel level < 15%
3. **High RPM Alert:** RPM > 6000 for > 5 minutes
4. **Extreme Acceleration:** > 5 m/s² for > 3 seconds

### Visual Indicators
- Red indicators for critical alerts
- Yellow indicators for warnings
- Smooth animations for state changes

---

## 9. Technology Dependencies

| Component | Package | Version |
|-----------|---------|---------|
| Web Framework | Streamlit | >= 1.28 |
| Charts | Plotly | >= 5.17 |
| API | FastAPI | >= 0.104 |
| Database | SQLAlchemy | >= 2.0 |
| Async | Uvicorn | >= 0.24 |
| Data Processing | Pandas | >= 2.0 |
| Utilities | Python-dotenv | >= 1.0 |

---

## 10. Development Timeline (MVP/POC)

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | Week 1 | API setup, data model, sample data generator |
| **Phase 2** | Week 2 | Dashboard layout, gauge components, basic charts |
| **Phase 3** | Week 3 | Real-time updates, alerts, data export |
| **Phase 4** | Week 4 | Testing, documentation, deployment |

---

## 11. Deployment (MVP)

### Development
```bash
# Terminal 1: Start API
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Start Dashboard
streamlit run src/dashboard/app.py --server.port=8501
```

### Access
- Dashboard: `http://localhost:8501`
- API Docs: `http://localhost:8000/docs`

### Database
- Development: SQLite (file-based, no setup needed)
- Location: `data/telemetry.db`

---

## 12. Limitations (MVP/POC)

- ❌ No user authentication
- ❌ No multi-vehicle dashboard
- ❌ No real Kafka/MQTT integration (simulated data only)
- ❌ No advanced ML-based anomaly detection
- ❌ No data persistence beyond 7 days
- ❌ No production monitoring or alerting
- ❌ Single-user concurrent access only

---

## 13. Future Enhancements (Production Roadmap)

- [ ] Multi-vehicle fleet dashboard
- [ ] User authentication & role-based access
- [ ] Real-time Kafka data ingestion
- [ ] Advanced anomaly detection (ML models)
- [ ] Mobile-responsive design
- [ ] Predictive maintenance alerts
- [ ] Data archival & compression
- [ ] Custom dashboard builder
- [ ] Alert notifications (email, SMS, Slack)
- [ ] Performance metrics & KPIs

---

## 14. Testing Strategy

### Unit Tests
- API endpoint response validation
- Data model serialization

### Integration Tests
- Dashboard ↔ API communication
- Database read/write operations

### Manual Tests
- Real-time data refresh (visual verification)
- Chart rendering with different data volumes
- Export to CSV and verify format

### Test Coverage
- Target: 70% (MVP level)

---

## 15. Success Criteria

✅ Dashboard loads and displays real-time data  
✅ Charts update automatically every 2 seconds  
✅ Alerts trigger correctly for threshold violations  
✅ Export to CSV works without errors  
✅ No crashes with simulated sensor data streams  
✅ Dashboard responsive to time range filtering  

---

## Appendix A: Sample Data Structure

```json
{
  "vehicle_id": "VEHICLE_001",
  "timestamp": "2026-10-05T10:30:45Z",
  "telemetry": {
    "speed_kmh": 72.5,
    "engine_temp_celsius": 87.3,
    "fuel_level_percent": 68,
    "rpm": 3200,
    "acceleration_mps2": 0.5,
    "engine_status": "running",
    "battery_voltage": 12.9
  },
  "anomalies": [],
  "alerts": []
}
```

---

**End of Document**
