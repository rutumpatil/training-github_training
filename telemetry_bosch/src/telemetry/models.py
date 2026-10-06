"""SQLAlchemy ORM models and Pydantic schemas for telemetry data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TelemetryORM(Base):
    """SQLAlchemy ORM model for vehicle telemetry data.
    
    Represents raw telemetry readings from vehicles with comprehensive
    vehicle performance metrics including speed, temperature, fuel level,
    RPM, battery voltage, and engine status.
    
    Attributes:
        id: Unique record identifier (auto-increment primary key)
        vehicle_id: Vehicle identifier (indexed for fast lookups)
        timestamp: Time of telemetry reading (indexed for time-series queries)
        speed: Vehicle speed in km/h (0-200)
        engine_temperature: Engine temperature in Celsius (0-120)
        fuel_level: Fuel tank level in percentage (0-100)
        rpm: Engine revolutions per minute (0-8000)
        battery_voltage: Battery voltage in volts (10-16)
        engine_status: Engine state ('running' or 'off')
        acceleration: Vehicle acceleration in m/s² (optional)
        warnings: Alert/warning messages (optional)
        created_at: Record creation timestamp (auto-populated)
        updated_at: Record last update timestamp (auto-populated)
    """

    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    speed = Column(Float, nullable=False)
    engine_temperature = Column(Float, nullable=False)
    fuel_level = Column(Float, nullable=False)
    rpm = Column(Integer, nullable=False)
    battery_voltage = Column(Float, nullable=False)
    engine_status = Column(String(20), nullable=False)
    acceleration = Column(Float, nullable=True)
    warnings = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        """Return string representation of telemetry record."""
        return (
            f"TelemetryORM(id={self.id}, vehicle_id={self.vehicle_id}, "
            f"timestamp={self.timestamp}, speed={self.speed})"
        )


class TelemetryCreate(BaseModel):
    """Pydantic schema for creating new telemetry records.
    
    Validates input data for POST requests to ensure all telemetry
    metrics are within acceptable ranges before database insertion.
    """

    vehicle_id: str = Field(..., min_length=1, max_length=50)
    timestamp: datetime
    speed: float = Field(..., ge=0, le=200)
    engine_temperature: float = Field(..., ge=0, le=120)
    fuel_level: float = Field(..., ge=0, le=100)
    rpm: int = Field(..., ge=0, le=8000)
    battery_voltage: float = Field(..., ge=10, le=16)
    engine_status: str = Field(..., pattern="^(running|off)$")
    acceleration: Optional[float] = Field(None)
    warnings: Optional[str] = Field(None, max_length=500)

    @field_validator("vehicle_id")
    @classmethod
    def validate_vehicle_id(cls, v: str) -> str:
        """Validate vehicle_id is not empty or whitespace."""
        if not v or v.isspace():
            raise ValueError("vehicle_id cannot be empty or whitespace")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Validate timestamp is not in the future."""
        if v > datetime.utcnow():
            raise ValueError("timestamp cannot be in the future")
        return v

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TelemetryUpdate(BaseModel):
    """Pydantic schema for updating telemetry records.
    
    Allows partial updates to telemetry records with the same
    validation as TelemetryCreate for modified fields.
    """

    speed: Optional[float] = Field(None, ge=0, le=200)
    engine_temperature: Optional[float] = Field(None, ge=0, le=120)
    fuel_level: Optional[float] = Field(None, ge=0, le=100)
    rpm: Optional[int] = Field(None, ge=0, le=8000)
    battery_voltage: Optional[float] = Field(None, ge=10, le=16)
    engine_status: Optional[str] = Field(None, pattern="^(running|off)$")
    acceleration: Optional[float] = Field(None)
    warnings: Optional[str] = Field(None, max_length=500)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TelemetryResponse(BaseModel):
    """Pydantic schema for telemetry API responses.
    
    Complete representation of a telemetry record including all fields
    and timestamps for external API consumption.
    """

    id: int
    vehicle_id: str
    timestamp: datetime
    speed: float
    engine_temperature: float
    fuel_level: float
    rpm: int
    battery_voltage: float
    engine_status: str
    acceleration: Optional[float] = None
    warnings: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True