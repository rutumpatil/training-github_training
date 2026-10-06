"""Custom exception classes for telemetry operations."""


class TelemetryException(Exception):
    """Base exception for telemetry operations."""

    pass


class VehicleNotFoundError(TelemetryException):
    """Raised when a vehicle is not found in the database."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle with ID '{vehicle_id}' not found")


class InvalidDateRangeError(TelemetryException):
    """Raised when the date range is invalid."""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(f"Invalid date range: {start_date} to {end_date}")


class DataValidationError(TelemetryException):
    """Raised when data validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for field '{field}': {message}")


class DatabaseError(TelemetryException):
    """Raised when a database operation fails."""

    def __init__(self, message: str):
        super().__init__(f"Database error: {message}")