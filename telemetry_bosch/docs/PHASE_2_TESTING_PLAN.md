# Phase 2 Testing Plan: API Layer
## Vehicle Telemetry Visualization MVP
## Automated Unit Testing with Parameterized Test Specifications

**Document Version:** 1.0  
**Phase:** 2 (API Layer)  
**Date:** 2026-10-05  
**Duration:** Week 2  
**Testing Framework:** pytest with parametrize, fixtures, mocks  

---

## Table of Contents
1. [Phase 2 Overview](#phase-2-overview)
2. [API Components Under Test](#api-components-under-test)
3. [Parameterized Test Specifications](#parameterized-test-specifications)
4. [Endpoint Testing Matrix](#endpoint-testing-matrix)
5. [Schema Validation Testing](#schema-validation-testing)
6. [Query Service Testing](#query-service-testing)
7. [Exception & Error Handling](#exception--error-handling)
8. [Mock & Fixture Strategy](#mock--fixture-strategy)
9. [Test Organization](#test-organization)
10. [Automation & CI/CD](#automation--cicd)
11. [Coverage Targets](#coverage-targets)
12. [Success Criteria](#success-criteria)

---

## Phase 2 Overview

**Objective:** Validate all API Layer components (FastAPI app, routes, schemas, query service, exceptions) using parameterized testing across boundary conditions, error scenarios, and valid input ranges.

**Scope:**
- FastAPI application initialization and middleware setup
- 4 REST API endpoints with multiple parameter combinations
- Pydantic schema validation for requests/responses
- TelemetryQueryService database queries
- Custom exception hierarchy and error handling

**Dependencies:**
- Phase 1 must be complete (Database + sample data)
- In-memory SQLite for isolated testing
- Mock dependencies (no real database calls in unit tests)

**Integration Points:**
- FastAPI routes → TelemetryQueryService (mocked in unit tests)
- TelemetryQueryService → Database (in-memory or mock)
- Exception handlers → Custom exception classes
- Schema validators → Pydantic models

---

## API Components Under Test

### 1. FastAPIApp (src/api/main.py)

**Responsibility:** Application initialization, middleware setup, exception handlers

**Test Scope:**
- App creation and configuration
- Middleware registration
- Exception handler registration
- CORS settings
- Route registration

**Parameterized Test Points:**
- Multiple CORS origin configurations
- Different log levels
- Various environment settings

---

### 2. TelemetryRouter (src/api/routes/telemetry.py)

**Responsibility:** Define 4 REST endpoints for telemetry data access

**Endpoints Under Test:**
1. **GET /api/telemetry/latest** - Latest vehicle telemetry
2. **GET /api/telemetry/history** - Historical data with date range
3. **GET /api/telemetry/export** - CSV export with filtering
4. **GET /api/vehicles** - List available vehicles

---

### 3. TelemetrySchema (src/api/schemas.py)

**Responsibility:** Pydantic models for request/response validation

**Schemas Under Test:**
- TelemetryResponse (latest data)
- TelemetryHistoryItem (historical records)
- ErrorResponse
- HealthResponse

---

### 4. TelemetryQueryService (src/telemetry/queries.py)

**Responsibility:** Database query logic for telemetry data

**Methods Under Test:**
- get_latest(vehicle_id: str)
- get_history(vehicle_id: str, hours: int, limit: int)
- get_all_vehicles()
- export_csv(vehicle_id: str, start_date, end_date)

---

### 5. Exception Handlers (src/api/exceptions.py)

**Responsibility:** Custom exceptions and error responses

**Exceptions Under Test:**
- VehicleNotFoundError (404)
- InvalidDateRangeError (400)
- DatabaseConnectionError (503)
- ExportError (500)

---

## Parameterized Test Specifications

### Test Specification Template (Per Component)

```
Component: {Name}
Module: {File Path}
Method/Function: {Name}
Test Category: {Unit/Integration}

Parameter Set {N}: {Scenario Description}
├─ Parameter Values: {input1, input2, ...}
├─ Expected Outcome: {assertion}
├─ Error Case: {exception type, if any}
├─ Mock Setup: {mocked dependencies}
├─ Test IDs: {param_case_1, param_case_2, ...}
└─ Coverage Target: {%}
```

---

## Endpoint Testing Matrix

### Endpoint 1: GET /api/telemetry/latest

**URL:** `/api/telemetry/latest`  
**Method:** GET  
**Purpose:** Retrieve latest telemetry record for a vehicle  
**Response Time Target:** < 200ms  

#### Parameter Set 1: Valid Vehicle ID
- **Parameters:** vehicle_id="VEHICLE_001"
- **Test Cases:**
  - vehicle_id="VEHICLE_001" → 200 OK, valid TelemetryResponse
  - vehicle_id="VEHICLE_002" → 200 OK, valid TelemetryResponse
  - vehicle_id="" (empty) → 400 Bad Request
  - vehicle_id=None (missing) → Defaults to first vehicle or 400
- **Response Schema Validation:** All fields present, correct types, ranges valid
- **Error Cases:**
  - Vehicle not in database → 404 VehicleNotFoundError
  - Database connection failure → 503 DatabaseConnectionError
- **Mock Setup:** Mock TelemetryQueryService.get_latest()
- **Test IDs:** latest_valid_vehicle_001, latest_valid_vehicle_002, latest_empty_id, latest_missing_id, latest_not_found, latest_db_error
- **Coverage Target:** 95%

#### Parameter Set 2: Response Content Validation
- **Expected Fields:** vehicle_id, timestamp, speed_kmh, engine_temp_celsius, fuel_level_percent, rpm, acceleration_mps2, engine_status, battery_voltage, warnings
- **Field Constraints:**
  - speed_kmh: 0-300 (numeric, float)
  - engine_temp_celsius: -50-150 (numeric, float)
  - fuel_level_percent: 0-100 (numeric, float)
  - rpm: 0-8000 (integer)
  - engine_status: "running" | "off" (string)
  - battery_voltage: 0-15 (numeric, float)
  - timestamp: ISO8601 datetime format
- **Test Cases:** Validate each field type and range
- **Test IDs:** response_speed_valid, response_speed_boundary, response_temp_valid, response_fuel_valid, response_status_valid, response_battery_valid, response_timestamp_format

#### Parameter Set 3: Cache Behavior
- **Scenario:** Multiple rapid requests should use cache
- **Parameters:** Same vehicle_id, rapid succession
- **Expected Behavior:** First call queries DB, subsequent calls use cached data
- **Cache TTL:** 2 seconds for latest data
- **Test IDs:** latest_cache_hit, latest_cache_miss, latest_cache_expiration

---

### Endpoint 2: GET /api/telemetry/history

**URL:** `/api/telemetry/history?vehicle_id={id}&hours={hours}&limit={limit}`  
**Method:** GET  
**Purpose:** Retrieve historical telemetry data with filtering  
**Response Time Target:** < 500ms  

#### Parameter Set 1: Query Parameter Validation

**Parameters:** vehicle_id, hours, limit

**Test Cases:**
- **Valid Ranges:**
  - vehicle_id="VEHICLE_001", hours=24, limit=100 → 200 OK, list of records
  - vehicle_id="VEHICLE_001", hours=1, limit=10 → 200 OK, limited records
  - vehicle_id="VEHICLE_001", hours=720, limit=1000 → 200 OK, max records
  
- **Boundary Values:**
  - hours=0 → 200 OK, empty list or current hour only
  - hours=1, limit=1 → 200 OK, 1 record
  - hours=720 (30 days max), limit=1000 (max) → 200 OK
  - hours=-1 → 400 Bad Request, InvalidDateRangeError
  - limit=0 → 400 Bad Request, InvalidDateRangeError
  - limit=-1 → 400 Bad Request, InvalidDateRangeError
  
- **Invalid Inputs:**
  - vehicle_id="" → 400 Bad Request
  - vehicle_id=None → 404 Not Found
  - hours="abc" → 400 Bad Request (type error)
  - limit="xyz" → 400 Bad Request (type error)
  - hours=721 (exceeds max) → 400 Bad Request
  - limit=1001 (exceeds max) → 400 Bad Request

- **Missing Parameters:**
  - No vehicle_id → 400 Bad Request (required)
  - No hours → Defaults to 24 (optional)
  - No limit → Defaults to 100 (optional)

**Test IDs:**
- history_valid_vehicle_001, history_valid_vehicle_002
- history_hours_0, history_hours_1, history_hours_max
- history_limit_1, history_limit_max
- history_hours_negative, history_limit_negative
- history_hours_type_error, history_limit_type_error
- history_hours_over_max, history_limit_over_max
- history_vehicle_empty, history_vehicle_missing
- history_default_hours, history_default_limit

**Coverage Target:** 90%

---

### Endpoint 3: GET /api/telemetry/export

**URL:** `/api/telemetry/export?vehicle_id={id}&start_date={date}&end_date={date}&format={format}`  
**Method:** GET  
**Purpose:** Export telemetry data as CSV or JSON  
**Response Type:** File download (text/csv)  
**Response Time Target:** < 1000ms  

#### Parameter Set 1: Export Format & Date Range

**Parameters:** vehicle_id, start_date, end_date, format

**Valid Test Cases:**
- vehicle_id="VEHICLE_001", start_date="2026-10-01", end_date="2026-10-05", format="csv" → 200 OK, CSV file
- vehicle_id="VEHICLE_001", start_date="2026-10-05", end_date="2026-10-05", format="csv" → 200 OK, single-day CSV
- vehicle_id="VEHICLE_001", format="json" → 200 OK, JSON format

**Boundary Test Cases:**
- start_date == end_date → 200 OK, single-day records
- start_date > end_date → 400 InvalidDateRangeError
- start_date == end_date == "2026-10-05" → 200 OK
- start_date > current_date → 400 Bad Request (future date)
- date range with 0 records → 200 OK, empty file with headers

**Test IDs:**
- export_valid_csv, export_valid_json
- export_single_day, export_date_equal
- export_start_after_end, export_future_date
- export_zero_records

**Coverage Target:** 85%

---

### Endpoint 4: GET /api/vehicles

**URL:** `/api/vehicles`  
**Method:** GET  
**Purpose:** List all vehicles in the database  
**Response Time Target:** < 100ms  

#### Parameter Set 1: Vehicle List Response

**Response Format:**
```json
{
  "vehicles": ["VEHICLE_001", "VEHICLE_002", "VEHICLE_003", ...]
}
```

**Test Cases:**
- Database has vehicles → 200 OK, list of vehicle IDs
- Database is empty → 200 OK, empty list
- Multiple vehicles (3, 10, 100) → All vehicles returned, sorted alphabetically

**Expected Behavior:**
- Vehicle list is sorted
- No duplicates
- All vehicle IDs are strings

**Test IDs:**
- vehicles_list_valid, vehicles_list_empty
- vehicles_list_count_3, vehicles_list_count_10
- vehicles_list_sorted, vehicles_list_no_duplicates
- vehicles_list_string_format

**Coverage Target:** 90%

---

## Schema Validation Testing

### TelemetryResponse Schema

**File:** src/api/schemas.py  
**Class:** TelemetryResponse  

#### Parameter Set 1: Field Type & Range Validation

| Field | Type | Range | Valid Examples | Invalid Examples |
|-------|------|-------|---|---|
| vehicle_id | str | N/A | "VEHICLE_001" | "", None |
| timestamp | datetime | ISO8601 | "2026-10-05T10:30:45Z" | "invalid", None |
| speed_kmh | float | 0-300 | 0, 150, 300 | -1, 301, None, "abc" |
| engine_temp_celsius | float | -50-150 | -50, 85.5, 100, 150 | -51, 151, None |
| fuel_level_percent | float | 0-100 | 0, 50, 100 | -1, 101, None |
| rpm | int | 0-8000 | 0, 4000, 8000 | -1, 8001, None |
| engine_status | str | "running"\|"off" | "running", "off" | "RUNNING", "stopped", "", None |
| battery_voltage | float | 0-15 | 0, 12.8, 15 | -1, 16, None |

**Test IDs:** schema_speed_valid, schema_speed_negative, schema_speed_over, schema_temp_min, schema_temp_critical, schema_fuel_empty, schema_fuel_full, schema_rpm_max, schema_status_valid, schema_status_case, schema_status_invalid, schema_battery_valid

**Coverage Target:** 95%

---

## Query Service Testing

### TelemetryQueryService.get_latest()

**File:** src/telemetry/queries.py  
**Method:** get_latest(vehicle_id: str) → Telemetry  

#### Parameter Set 1: Valid Vehicle ID

**Test Cases:**
- vehicle_id="VEHICLE_001" → Returns latest Telemetry record
- vehicle_id="VEHICLE_002" → Returns latest for different vehicle
- Multiple calls same vehicle → Returns same record (unless new data inserted)

**Expected Behavior:**
- Query uses index: vehicle_id, timestamp DESC
- Single record returned (LIMIT 1)
- Record is most recent (ORDER BY timestamp DESC)

**Test IDs:** query_latest_vehicle_001, query_latest_vehicle_002, query_latest_deterministic

**Mocks:** Database session (in-memory SQLite)  
**Coverage Target:** 90%

---

### TelemetryQueryService.get_history()

**File:** src/telemetry/queries.py  
**Method:** get_history(vehicle_id: str, hours: int = 24, limit: int = 100) → List[Telemetry]  

#### Parameter Set 1: Time Range Filtering

**Current Time:** 2026-10-05 10:00:00

**Test Cases:**
- hours=1 → Returns records from last 1 hour (2026-10-05 09:00:00 to 10:00:00)
- hours=24 → Returns records from last 24 hours
- hours=720 → Returns records from last 30 days

**Expected Behavior:**
- Query filters by: vehicle_id AND timestamp > (now - hours)
- Results ordered by timestamp (DESC or ASC, consistent)
- No records outside time range

**Test IDs:** query_history_1hour, query_history_24hours, query_history_30days

#### Parameter Set 2: Limit & Offset

**Test Cases:**
- limit=10 → Max 10 records returned
- limit=100 → Max 100 records returned
- limit=1000 → Max 1000 records returned
- 50 records in DB, limit=100 → Returns all 50
- 150 records in DB, limit=100 → Returns exactly 100 (latest)

**Test IDs:** query_history_limit_10, query_history_limit_100, query_history_under_limit, query_history_over_limit

**Fixtures:** Sample data with various timestamps and vehicles  
**Coverage Target:** 85%

---

## Exception & Error Handling

### Custom Exception Classes

**File:** src/api/exceptions.py  

#### Test Specification: VehicleNotFoundError

**HTTP Status Code:** 404  
**Message Format:** "Vehicle {vehicle_id} not found in database"

**Test Cases:**
- Raised when vehicle_id doesn't exist
- Exception message includes vehicle_id
- Returns 404 to client with correct JSON error response

**Test IDs:** exception_vehicle_not_found_404, exception_vehicle_not_found_message

#### Test Specification: InvalidDateRangeError

**HTTP Status Code:** 400  
**Message Format:** "Invalid date range: {start_date} to {end_date}"

**Test Cases:**
- Raised when start_date > end_date
- Exception message includes both dates
- Returns 400 to client

**Test IDs:** exception_invalid_date_range_400, exception_invalid_date_range_message

---

## Mock & Fixture Strategy

### Database Fixtures (tests/fixtures/database.py)

#### Fixture 1: In-Memory SQLite Database
- Initialize schema with Telemetry, Alert, AnomalyLog tables
- Insert sample data:
  - VEHICLE_001: 100 records (24-hour window)
  - VEHICLE_002: 50 records (24-hour window)
  - VEHICLE_003: 1000 records (30-day window)
  - Anomalous records (overheat, low fuel, high RPM)

#### Fixture 2: Sample Telemetry Records
- Pre-made records with various properties
- Includes: normal, anomalous, boundary value records

### API Mocks (tests/fixtures/mocks.py)

#### Mock 1: TelemetryQueryService
- Mock get_latest()
- Mock get_history()
- Mock export_csv()
- Mock get_all_vehicles()

#### Mock 2: FastAPI Test Client
- Initialize FastAPI app
- Override dependencies with mocks
- Return TestClient

---

## Test Organization

### Unit Tests Structure

**File:** tests/unit/test_telemetry_router.py

```python
class TestGetLatestTelemetry:
    @pytest.mark.parametrize("vehicle_id,expected_status", [
        ("VEHICLE_001", 200),
        ("VEHICLE_002", 200),
        ("NONEXISTENT", 404),
        ("", 400),
    ])
    def test_get_latest_valid_vehicle(self, api_client, vehicle_id, expected_status):
        # Arrange
        # Act
        response = api_client.get(f"/api/telemetry/latest?vehicle_id={vehicle_id}")
        # Assert
        assert response.status_code == expected_status
```

**File:** tests/unit/test_schemas.py

```python
class TestTelemetryResponseSchema:
    @pytest.mark.parametrize("speed,is_valid", [
        (0, True),
        (150, True),
        (300, True),
        (-1, False),
        (301, False),
        (None, False),
        ("abc", False),
    ])
    def test_speed_validation(self, speed, is_valid):
        # Test speed field validation
        pass
```

---

## Coverage Targets

| Module | Target | Priority |
|--------|--------|----------|
| src/api/main.py | 80% | High |
| src/api/routes/telemetry.py | 85% | Critical |
| src/api/schemas.py | 95% | Critical |
| src/telemetry/queries.py | 85% | High |
| src/api/exceptions.py | 90% | High |
| **Overall** | **85%** | **Critical** |

---

## Success Criteria

✅ **Phase 2 Testing Complete When:**

1. **All Endpoints Tested** - 200 OK, 404, 400, 503 scenarios covered
2. **Schema Validation Comprehensive** - All fields validated, boundary values tested
3. **Query Service Robust** - Date filtering, record limiting, vehicle filtering tested
4. **Exception Handling Consistent** - Custom exceptions map to correct HTTP status codes
5. **Coverage Metrics Met** - 85%+ line coverage for all modules
6. **Tests Run Deterministically** - All tests pass/fail consistently
7. **Parameterized Testing Used** - No duplicate test functions
8. **CI/CD Integration Ready** - Tests run automatically on every commit

---

**Phase 2 Testing Document Status:** READY FOR IMPLEMENTATION  
**Test Framework:** pytest with parametrize, fixtures, mocks  
**Automation:** pytest-xdist, pytest-cov, CI/CD ready  
**Next Step:** Begin unit test implementation (tests/unit/)
