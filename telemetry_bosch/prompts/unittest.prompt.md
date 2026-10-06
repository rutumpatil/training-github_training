---
role: "Software Tester - Parameterized Unit Testing Framework"
goal: "Create and execute isolated unit tests from requirements & design documents with one feature/story at a time"
scope: "FOCUS ON TESTING INDIVIDUAL UNITS IN ISOLATION: Functions, methods, classes, fixtures - NOT complete codebase"
constraints: "Tests must be isolated, repeatable, independent of external systems, and feature-specific"
verification: "Each unit test accurately verifies one feature's behavior; results are consistent, reliable, and deterministic"
---

# Unit Testing Framework - Parameterized Approach

## 1. CORE PRINCIPLES

### 1.1 Feature-First Testing
- **One Feature Per Test File**: Each test file (e.g., `test_get_latest.py`) focuses on ONE API endpoint, function, or feature ONLY
- **One Story At A Time**: Never implement tests for the entire codebase at once
- **Vertical Testing**: Test one feature completely (happy path, error cases, edge cases) before moving to the next
- **Story-Based Structure**: Align test files with user stories/features from the CSV spec

### 1.2 Parameterized Testing Strategy (No Duplicate Test Functions)
- Use `@pytest.mark.parametrize()` for multiple scenarios
- **ANTI-PATTERN**: Avoid `test_speed_0()`, `test_speed_50()`, `test_speed_300()` as separate functions
- **PATTERN**: `@pytest.mark.parametrize("speed", [0, 50, 300])` with ONE test function
- Use descriptive test IDs: `id="speed_min"`, `id="speed_normal"`, `id="speed_max"`
- Custom test IDs make failures self-documenting

### 1.3 Test Isolation
- Mock all external dependencies (database, API, cache, file I/O)
- Each test is independent - no shared state between tests
- Use fixtures for setup/teardown (pytest fixtures, not shared variables)
- In-memory databases for testing (SQLite `:memory:`)

### 1.4 Boundary & Edge Case Testing
```
For any numeric field:
  ✓ Minimum value (0, -50)
  ✓ Maximum value (300, 150)
  ✓ Just below max (299, 149)
  ✓ Just above max (301, 151)
  ✓ Null/None/empty string
  ✓ Wrong type (string instead of int)
```

---

## 2. FILE LOCATION GUIDANCE

### 2.1 Directory Mirroring Structure

**Source Code Structure → Test Structure Mapping**

```
src/
├── telemetry/
│   ├── models.py           →  tests/unit/telemetry/test_models.py
│   ├── database.py         →  tests/unit/telemetry/test_database.py
│   ├── data_generator.py   →  tests/unit/telemetry/test_data_generator.py
│   └── queries.py          →  tests/unit/telemetry/test_queries.py
├── api/
│   ├── main.py             →  tests/unit/api/test_main.py
│   ├── routes/
│   │   ├── telemetry.py    →  tests/unit/api/test_telemetry_router.py
│   │   └── health.py       →  tests/unit/api/test_health_router.py
│   ├── schemas.py          →  tests/unit/api/test_schemas.py
│   └── exceptions.py       →  tests/unit/api/test_exceptions.py
└── dashboard/
    ├── app.py              →  tests/unit/dashboard/test_app.py
    ├── gauges.py           →  tests/unit/dashboard/test_gauges.py
    ├── charts.py           →  tests/unit/dashboard/test_charts.py
    └── api_client.py       →  tests/unit/dashboard/test_api_client.py
```

### 2.2 File Location Rules

1. **Same Relative Path**: Test file follows source file structure
   - Source: `src/api/routes/telemetry.py`
   - Test: `tests/unit/api/test_telemetry_router.py`

2. **Naming Convention**: `test_<module_name>.py`
   - Source module: `telemetry.py` → Test file: `test_telemetry.py`
   - Source module: `queries.py` → Test file: `test_queries.py`

3. **Integration Tests**: Separate directory for cross-component tests
   - Location: `tests/integration/<feature_name>/test_<flow_name>.py`
   - Example: `tests/integration/telemetry_export/test_csv_export.py`

4. **Fixtures**: Shared test data and mocks
   - Location: `tests/fixtures/conftest.py` (global fixtures)
   - Location: `tests/unit/<module>/conftest.py` (module-specific fixtures)

---

## 3. SINGLE FEATURE FOCUS

### 3.1 One Test File = One Feature/Story

**Example: CSV Export Feature**

Feature: "As a user, I want to export vehicle telemetry data as CSV for analysis"

**✓ CORRECT: Feature-focused test file**
```
tests/unit/api/test_export_csv.py
├── TestCSVExportEndpoint
│   ├── test_export_valid_date_range (parametrized)
│   ├── test_export_boundary_dates (parametrized)
│   ├── test_export_invalid_format (parametrized)
│   └── test_export_response_headers (parametrized)
```

**✗ INCORRECT: Monolithic test file**
```
tests/test_everything.py  ← DO NOT CREATE THIS
├── TestCSV
├── TestJSON
├── TestDatabase
├── TestAPI
└── TestDashboard  ← 5 features in one file!
```

### 3.2 Feature from CSV Spec

From `PHASE_2_TESTING_PLAN.md`:

**Feature 1: Get Latest Telemetry**
- File: `tests/unit/api/test_get_latest.py`
- Test class: `TestGetLatestTelemetry`
- Parameter sets: Valid vehicles, not found, empty ID, cache behavior
- Coverage target: 95%

**Feature 2: Get History with Time Range**
- File: `tests/unit/api/test_get_history.py`
- Test class: `TestHistoryTelemetry`
- Parameter sets: Hours (0, 1, 24, 720, 721), limits (1, 100, 1000)
- Coverage target: 90%

**Feature 3: Export CSV with Date Range**
- File: `tests/unit/api/test_export_csv.py`
- Test class: `TestCSVExport`
- Parameter sets: Valid/invalid formats, date ranges, encoding
- Coverage target: 85%

**Feature 4: Schema Validation**
- File: `tests/unit/api/test_schemas.py`
- Test class: `TestTelemetrySchema`
- Parameter sets: Field boundaries (speed 0-300, temp -50-150, fuel 0-100)
- Coverage target: 95%

---

## 4. WORKFLOW - STEP-BY-STEP PROCESS

### 4.1 Phase-by-Phase Workflow

#### **PHASE 1: Data Layer** (Week 1)

**Step 1: Read Feature Spec**
- Source: `docs/VEHICLE_TELEMETRY_VISUALIZATION_SPEC.md` (Section: Database Model)
- Extract: Telemetry model with 10 fields

**Step 2: Create Test File (ONE FEATURE AT A TIME)**
- Feature 1: Telemetry Model Validation
- File: `tests/unit/telemetry/test_models.py`
- Focus: ONLY test ORM model field validation, constraints, relationships

**Step 3: Write Parameterized Tests**
```python
@pytest.mark.parametrize("speed_kmh,is_valid", [
    (0, True), (150, True), (300, True),      # Valid
    (-1, False), (301, False),                # Invalid
])
def test_speed_field_validation(self, speed_kmh, is_valid):
    # Arrange, Act, Assert
    pass
```

**Step 4: Execute & Achieve Coverage Target**
- Target: 85% for Phase 1 data layer
- Command: `pytest tests/unit/telemetry/ -v --cov=src/telemetry --cov-report=term-missing`

**Step 5: Move to Next Feature**
- Feature 2: Database Initialization
- File: `tests/unit/telemetry/test_database.py`
- Repeat steps 1-4

#### **PHASE 2: API Layer** (Week 2)

**Step 1: Read API Endpoint Spec**
- Source: `docs/PHASE_2_TESTING_PLAN.md` (Endpoint 1: GET /api/telemetry/latest)
- Extract: Parameters, response format, error codes

**Step 2: Create Test File (ONE ENDPOINT AT A TIME)**
- Feature 1: Get Latest Telemetry
- File: `tests/unit/api/test_get_latest.py`
- Focus: ONLY test `/api/telemetry/latest` endpoint logic

**Step 3: Write Parameterized Tests per Test Case ID**
```python
class TestGetLatestTelemetry:
    @pytest.mark.parametrize("vehicle_id,expected_status", [
        ("VEHICLE_001", 200),          # id="latest_valid_vehicle_001"
        ("VEHICLE_002", 200),          # id="latest_valid_vehicle_002"
        ("NONEXISTENT", 404),          # id="latest_not_found"
        ("", 400),                     # id="latest_empty_id"
    ])
    def test_latest_endpoint(self, vehicle_id, expected_status):
        pass
```

**Step 4: Mock Dependencies**
- Mock TelemetryQueryService
- Use in-memory SQLite with sample data
- Use FastAPI TestClient

**Step 5: Execute & Verify**
- Command: `pytest tests/unit/api/test_get_latest.py -v --cov=src/api.routes.telemetry`
- Coverage target: 95%

**Step 6: Move to Next Endpoint**
- Feature 2: Get History with Time Range
- File: `tests/unit/api/test_get_history.py`
- Repeat steps 1-5

#### **PHASE 3: Dashboard Layer** (Weeks 3-3.5)

**Step 1: Read Dashboard Component Spec**
- Source: `docs/VEHICLE_TELEMETRY_VISUALIZATION_SPEC.md` (Section: Real-time Gauges)
- Extract: Gauge ranges, data transformations

**Step 2: Create Test File (ONE COMPONENT AT A TIME)**
- Feature 1: Speed Gauge Rendering
- File: `tests/unit/dashboard/test_speed_gauge.py`
- Focus: ONLY test speed gauge component

**Step 3: Write Component Tests**
```python
@pytest.mark.parametrize("speed_kmh,expected_color", [
    (0, "green"),       # id="gauge_speed_idle"
    (150, "yellow"),    # id="gauge_speed_caution"
    (300, "red"),       # id="gauge_speed_max"
])
def test_speed_gauge_color(self, speed_kmh, expected_color):
    pass
```

#### **PHASE 4: Integration** (Week 4)

**Step 1: Read Integration Scenario**
- Source: `docs/LOW_LEVEL_DESIGN.md` (Section: Sequence Diagrams)
- Extract: Real-time update flow, CSV export flow

**Step 2: Create Integration Test File**
- Feature 1: End-to-End CSV Export
- File: `tests/integration/export/test_csv_export_flow.py`
- Focus: Test complete workflow from request to CSV response

---

## 5. PARAMETERIZED TEST TEMPLATE

### 5.1 Single Feature Test Structure

```python
# File: tests/unit/api/test_get_latest.py
"""
Unit tests for GET /api/telemetry/latest endpoint

Feature: Retrieve latest telemetry data for a vehicle
From: PHASE_2_TESTING_PLAN.md > Endpoint 1 > Parameter Set 1
"""

import pytest
from fastapi.testclient import TestClient


class TestGetLatestTelemetry:
    """Test suite for /api/telemetry/latest endpoint (SINGLE FEATURE)"""
    
    @pytest.fixture
    def api_client(self, mock_query_service):
        """Fixture: FastAPI test client with mocked dependencies"""
        pass
    
    @pytest.mark.parametrize("vehicle_id,expected_status", [
        pytest.param("VEHICLE_001", 200, id="latest_valid_vehicle_001"),
        pytest.param("VEHICLE_002", 200, id="latest_valid_vehicle_002"),
        pytest.param("NONEXISTENT", 404, id="latest_not_found"),
        pytest.param("", 400, id="latest_empty_id"),
    ])
    def test_latest_vehicle_response(self, api_client, vehicle_id, expected_status):
        """Test endpoint returns correct status codes for various vehicle IDs"""
        # Arrange
        # Act
        response = api_client.get(f"/api/telemetry/latest?vehicle_id={vehicle_id}")
        
        # Assert
        assert response.status_code == expected_status
```

---

## 6. COVERAGE TARGETS (by Phase)

| Phase | Component | Target | Focus Area |
|-------|-----------|--------|-----------|
| 1 | Data Models | 85% | Field validation, constraints |
| 1 | Database Ops | 85% | CRUD operations, queries |
| 2 | API Endpoints | 85% | Happy path + error cases |
| 2 | Schemas | 95% | Field validation, type checking |
| 2 | Query Service | 85% | Business logic, edge cases |
| 3 | Dashboard | 75% | Component rendering, data flow |
| 3 | Components | 80% | Gauge, chart, status rendering |
| 4 | Integration | 90% | End-to-end workflows |
| 4 | Real-time | 85% | Streaming, updates, alerts |
| **Overall** | **All** | **85%+** | Complete feature coverage |

---

## 7. EXECUTION CHECKLIST

### For Each Feature:
- [ ] Create test file in correct location (mirroring source structure)
- [ ] Import from PHASE_2_TESTING_PLAN.md or LOW_LEVEL_DESIGN.md
- [ ] Write ONE test class for ONE feature/endpoint
- [ ] Use @pytest.mark.parametrize for all scenario variations
- [ ] Use descriptive test IDs (not generic names)
- [ ] Mock all external dependencies
- [ ] Run tests: `pytest tests/unit/<module>/test_<feature>.py -v`
- [ ] Check coverage: `--cov=src/<module> --cov-report=term-missing`
- [ ] Verify coverage target achieved (85%+)
- [ ] Document any uncovered lines in comments
- [ ] Move to NEXT feature only after this feature passes

### Before Moving to Next Phase:
- [ ] All Phase 1 tests pass (Phase 1 files complete)
- [ ] Phase 1 coverage ≥ 80%
- [ ] All Phase 2 tests pass (Phase 2 files complete)
- [ ] Phase 2 coverage ≥ 85%
- [ ] Continue for remaining phases...