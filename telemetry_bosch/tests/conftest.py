"""
pytest configuration and shared fixtures for Vehicle Telemetry Visualization MVP

This file contains:
- Global pytest configuration
- Shared fixtures for database, API client, and mocks
- Test data factories
"""

import pytest
from typing import Generator, List
from datetime import datetime, timedelta
import tempfile
import sqlite3
from pathlib import Path


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def database_path() -> str:
    """Create temporary database file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        return f.name


@pytest.fixture(scope="session")
def telemetry_schema() -> str:
    """SQL schema for telemetry database"""
    return """
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
    """


@pytest.fixture(scope="session")
def sample_telemetry_data() -> List[dict]:
    """Sample telemetry records for testing"""
    base_time = datetime(2026, 10, 5, 10, 0, 0)
    records = []
    
    # VEHICLE_001: 100 records over 24 hours
    for i in range(100):
        timestamp = base_time - timedelta(hours=24-i*0.24)
        records.append({
            'vehicle_id': 'VEHICLE_001',
            'timestamp': timestamp.isoformat() + 'Z',
            'speed_kmh': 60 + (i % 40),
            'engine_temp_celsius': 85 + (i % 30),
            'fuel_level_percent': 80 - (i % 30),
            'rpm': 2500 + (i % 2000),
            'acceleration_mps2': 0.5 + (i % 2),
            'engine_status': 'running',
            'battery_voltage': 12.5 + (i % 3) * 0.1,
            'is_anomaly': i % 20 == 0
        })
    
    # VEHICLE_002: 50 records over 24 hours
    for i in range(50):
        timestamp = base_time - timedelta(hours=24-i*0.48)
        records.append({
            'vehicle_id': 'VEHICLE_002',
            'timestamp': timestamp.isoformat() + 'Z',
            'speed_kmh': 70 + (i % 30),
            'engine_temp_celsius': 80 + (i % 40),
            'fuel_level_percent': 75 - (i % 25),
            'rpm': 3000 + (i % 1500),
            'acceleration_mps2': 0.3 + (i % 1.5),
            'engine_status': 'running',
            'battery_voltage': 12.8 + (i % 2) * 0.1,
            'is_anomaly': i % 25 == 0
        })
    
    return records


# ============================================================================
# TEST PARAMETERS & MARKERS
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for API endpoints")
    config.addinivalue_line("markers", "slow: Tests that run slowly")
    config.addinivalue_line("markers", "parametrize: Parameterized tests")


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on file location"""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Add cleanup logic here if needed


# ============================================================================
# LOGGING & OUTPUT
# ============================================================================

@pytest.fixture(scope="session")
def pytest_configure():
    """Configure pytest settings"""
    return {
        'python_files': 'test_*.py',
        'python_classes': 'Test*',
        'python_functions': 'test_*',
        'testpaths': ['tests'],
        'addopts': [
            '--verbose',
            '--strict-markers',
            '--tb=short',
            '--cov=src',
            '--cov-report=html',
            '--cov-report=term-missing',
        ]
    }
