"""Unit tests for telemetry ORM models and Pydantic schemas.

Tests cover:
- SQLAlchemy model creation and field defaults
- Pydantic schema validation and field boundaries
- Type coercion and error handling
- Timestamp validation
"""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.telemetry.models import (
    TelemetryCreate,
    TelemetryORM,
    TelemetryResponse,
    TelemetryUpdate,
)


class TestTelemetryORM:
    """Test SQLAlchemy ORM model for telemetry."""

    def test_telemetry_orm_creation(self):
        """Test creating a valid TelemetryORM instance."""
        record = TelemetryORM(
            vehicle_id="VEH001",
            timestamp=datetime.utcnow(),
            speed=100.0,
            engine_temperature=80.0,
            fuel_level=50.0,
            rpm=3000,
            battery_voltage=12.5,
            engine_status="running",
            acceleration=2.5,
            warnings=None,
        )

        assert record.vehicle_id == "VEH001"
        assert record.speed == 100.0
        assert record.engine_temperature == 80.0
        assert record.fuel_level == 50.0
        assert record.rpm == 3000
        assert record.battery_voltage == 12.5
        assert record.engine_status == "running"
        assert record.acceleration == 2.5
        assert record.warnings is None

    def test_telemetry_orm_defaults(self):
        """Test that created_at and updated_at default to current time."""
        now = datetime.utcnow()
        record = TelemetryORM(
            vehicle_id="VEH001",
            timestamp=now,
            speed=50.0,
            engine_temperature=70.0,
            fuel_level=75.0,
            rpm=2000,
            battery_voltage=12.0,
            engine_status="running",
        )

        assert record.created_at is not None
        assert record.updated_at is not None
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)

    def test_telemetry_orm_repr(self):
        """Test string representation of TelemetryORM."""
        now = datetime.utcnow()
        record = TelemetryORM(
            id=1,
            vehicle_id="VEH001",
            timestamp=now,
            speed=100.0,
            engine_temperature=80.0,
            fuel_level=50.0,
            rpm=3000,
            battery_voltage=12.5,
            engine_status="running",
        )

        repr_str = repr(record)
        assert "TelemetryORM" in repr_str
        assert "VEH001" in repr_str
        assert "100.0" in repr_str

    @pytest.mark.parametrize(
        "speed,valid",
        [
            (0, True),
            (100, True),
            (200, True),
            (-1, False),
            (201, False),
        ],
        ids=[
            "speed_min_valid",
            "speed_mid_valid",
            "speed_max_valid",
            "speed_negative_invalid",
            "speed_over_max_invalid",
        ],
    )
    def test_telemetry_create_speed_boundaries(self, speed, valid):
        """Test TelemetryCreate validation with speed boundary cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": speed,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.speed == speed
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    @pytest.mark.parametrize(
        "temp,valid",
        [
            (0, True),
            (80, True),
            (120, True),
            (-1, False),
            (121, False),
        ],
        ids=[
            "temp_min_valid",
            "temp_mid_valid",
            "temp_max_valid",
            "temp_negative_invalid",
            "temp_over_max_invalid",
        ],
    )
    def test_telemetry_create_temperature_boundaries(self, temp, valid):
        """Test TelemetryCreate validation with engine temperature boundary cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": temp,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.engine_temperature == temp
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    @pytest.mark.parametrize(
        "fuel,valid",
        [
            (0, True),
            (50, True),
            (100, True),
            (-1, False),
            (101, False),
        ],
        ids=[
            "fuel_min_valid",
            "fuel_mid_valid",
            "fuel_max_valid",
            "fuel_negative_invalid",
            "fuel_over_max_invalid",
        ],
    )
    def test_telemetry_create_fuel_boundaries(self, fuel, valid):
        """Test TelemetryCreate validation with fuel level boundary cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": fuel,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.fuel_level == fuel
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    @pytest.mark.parametrize(
        "rpm,valid",
        [
            (0, True),
            (3000, True),
            (8000, True),
            (-100, False),
            (8001, False),
        ],
        ids=[
            "rpm_min_valid",
            "rpm_mid_valid",
            "rpm_max_valid",
            "rpm_negative_invalid",
            "rpm_over_max_invalid",
        ],
    )
    def test_telemetry_create_rpm_boundaries(self, rpm, valid):
        """Test TelemetryCreate validation with RPM boundary cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": rpm,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.rpm == rpm
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    @pytest.mark.parametrize(
        "voltage,valid",
        [
            (10.0, True),
            (12.5, True),
            (16.0, True),
            (9.9, False),
            (16.1, False),
        ],
        ids=[
            "voltage_min_valid",
            "voltage_mid_valid",
            "voltage_max_valid",
            "voltage_under_min_invalid",
            "voltage_over_max_invalid",
        ],
    )
    def test_telemetry_create_voltage_boundaries(self, voltage, valid):
        """Test TelemetryCreate validation with battery voltage boundary cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": voltage,
            "engine_status": "running",
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.battery_voltage == voltage
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    @pytest.mark.parametrize(
        "status,valid",
        [
            ("running", True),
            ("off", True),
            ("idle", False),
            ("RUNNING", False),
            ("", False),
        ],
        ids=[
            "status_running_valid",
            "status_off_valid",
            "status_invalid_value",
            "status_uppercase_invalid",
            "status_empty_invalid",
        ],
    )
    def test_telemetry_create_engine_status(self, status, valid):
        """Test TelemetryCreate validation with engine status cases."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": status,
        }

        if valid:
            record = TelemetryCreate(**data)
            assert record.engine_status == status
        else:
            with pytest.raises(ValidationError):
                TelemetryCreate(**data)

    def test_telemetry_create_timestamp_in_future_invalid(self):
        """Test that TelemetryCreate rejects timestamps in the future."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        data = {
            "vehicle_id": "VEH001",
            "timestamp": future_time,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        with pytest.raises(ValidationError):
            TelemetryCreate(**data)

    def test_telemetry_create_empty_vehicle_id_invalid(self):
        """Test that TelemetryCreate rejects empty vehicle_id."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        with pytest.raises(ValidationError):
            TelemetryCreate(**data)

    def test_telemetry_create_whitespace_vehicle_id_invalid(self):
        """Test that TelemetryCreate rejects whitespace-only vehicle_id."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "   ",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        with pytest.raises(ValidationError):
            TelemetryCreate(**data)

    def test_telemetry_create_optional_fields(self):
        """Test that optional fields can be omitted."""
        now = datetime.utcnow()
        data = {
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
        }

        record = TelemetryCreate(**data)
        assert record.acceleration is None
        assert record.warnings is None

    def test_telemetry_update_partial_fields(self):
        """Test that TelemetryUpdate allows partial updates."""
        data = {
            "speed": 75.0,
            "fuel_level": 25.0,
        }

        record = TelemetryUpdate(**data)
        assert record.speed == 75.0
        assert record.fuel_level == 25.0
        assert record.engine_temperature is None
        assert record.rpm is None

    @pytest.mark.parametrize(
        "update_speed,valid",
        [
            (0, True),
            (150, True),
            (200, True),
            (-5, False),
            (250, False),
        ],
        ids=[
            "update_speed_min_valid",
            "update_speed_mid_valid",
            "update_speed_max_valid",
            "update_speed_negative_invalid",
            "update_speed_over_max_invalid",
        ],
    )
    def test_telemetry_update_speed_boundaries(self, update_speed, valid):
        """Test TelemetryUpdate validation with speed boundary cases."""
        data = {"speed": update_speed}

        if valid:
            record = TelemetryUpdate(**data)
            assert record.speed == update_speed
        else:
            with pytest.raises(ValidationError):
                TelemetryUpdate(**data)

    def test_telemetry_response_all_fields(self):
        """Test TelemetryResponse schema with all fields populated."""
        now = datetime.utcnow()
        data = {
            "id": 1,
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
            "acceleration": 2.5,
            "warnings": "None",
            "created_at": now,
            "updated_at": now,
        }

        record = TelemetryResponse(**data)
        assert record.id == 1
        assert record.vehicle_id == "VEH001"
        assert record.speed == 100.0
        assert record.acceleration == 2.5
        assert record.warnings == "None"

    def test_telemetry_response_optional_fields(self):
        """Test TelemetryResponse schema without optional fields."""
        now = datetime.utcnow()
        data = {
            "id": 1,
            "vehicle_id": "VEH001",
            "timestamp": now,
            "speed": 100.0,
            "engine_temperature": 80.0,
            "fuel_level": 50.0,
            "rpm": 3000,
            "battery_voltage": 12.5,
            "engine_status": "running",
            "created_at": now,
            "updated_at": now,
        }

        record = TelemetryResponse(**data)
        assert record.acceleration is None
        assert record.warnings is None
        assert record.id == 1
        assert record.vehicle_id == "VEH001"
        assert record.speed == 100.0
        assert record.engine_temperature == 80.0
        assert record.fuel_level == 50.0
        assert record.rpm == 3000
        assert record.battery_voltage == 12.5
        assert record.engine_status == "running"
        assert record.created_at == now
        assert record.updated_at == now 