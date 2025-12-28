# pricing_server.py
"""
Pricing Service for DG Do - Khujand, Tajikistan

This gRPC service calculates trip fares based on a dynamically loaded YAML pricing
configuration. It supports:
- Zone-based pricing overrides
- Time-of-day multipliers (peak hours, night, etc.)
- A/B testing of pricing strategies
- Cash rounding to common local denominations
- Commission calculations
"""

import grpc
from concurrent import futures
import uuid
import datetime
from decimal import Decimal

from pricing_pb2_grpc import PricingServiceServicer, add_PricingServiceServicer_to_server
from pricing_pb2 import PriceCalculationRequest, PriceCalculationResponse

from pricing_config_loader import PricingConfig


class PricingService(PricingServiceServicer):
    """
    Implementation of the PricingService gRPC server.

    Uses PricingConfig to load, validate, and retrieve active pricing configuration.
    """
    def __init__(self, config_path: str):
        """
        Initialize the PricingService with path to the YAML configuration.

        Args:
            config_path (str): Path to pricing_config.yaml
        """
        # Load configuration with automatic reload every 30 seconds
        self.config_loader = PricingConfig(config_path, reload_interval=30)

    def CalculatePrice(self, request: PriceCalculationRequest, context):
        """
        Calculate the passenger fare and driver payout for a trip request.

        Steps:
        1. Fetch active pricing configuration (zone + current time).
        2. Compute base, distance, and time fare.
        3. Apply surge multiplier (time-based or zone-specific).
        4. Round to nearest acceptable cash denomination.
        5. Compute platform commission and driver payout.
        """
        # Extract zone from request metadata (optional)
        zone = request.metadata.data.get("zone")
        current_hour = datetime.datetime.utcnow().hour

        # Fetch active pricing configuration for this request
        cfg = self.config_loader.get_active_config(zone=zone, current_hour=current_hour)

        # Convert distance and time to units for pricing
        distance_km = request.estimated_distance_meters / 1000
        time_min = request.estimated_duration_seconds / 60

        # Base fare + distance fare + time fare
        base_fare = Decimal(cfg.get("base_fare_tjs", 500))
        distance_fare = Decimal(cfg.get("per_km_rate_tjs", 2.0)) * Decimal(distance_km)
        time_fare = Decimal(cfg.get("per_min_rate_tjs", 0.5)) * Decimal(time_min)
        subtotal = base_fare + distance_fare + time_fare

        # Apply surge multiplier
        total = subtotal * Decimal(cfg.get("surge_multiplier", 1.0))

        # Round total to nearest acceptable denomination
        rounding_options = cfg.get("rounding_tjs", [0.5, 1, 3, 5])
        rounded_total = min(rounding_options, key=lambda x: abs(x - total))

        # Calculate platform commission and driver payout
        commission_percent = Decimal(cfg.get("commission_percent", 20))
        commission = total * commission_percent / Decimal(100)
        driver_payout = total - commission

        # Return gRPC response
        return PriceCalculationResponse(
            trip_request_id=request.trip_request_id,
            calculation_id=str(uuid.uuid4()),  # unique ID per calculation
            passenger_fare_total=float(rounded_total),
            driver_payout_total=float(driver_payout),
            platform_commission=float(commission),
            pricing_model_version=self.config_loader.config.get("version", "v1"),
        )


def serve():
    """
    Start the gRPC server and listen for incoming pricing requests.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register PricingService to gRPC server
    add_PricingServiceServicer_to_server(PricingService("pricing_config.yaml"), server)
    
    # Bind to port 50056
    server.add_insecure_port('[::]:50056')
    server.start()
    print("✅ PricingService running on port 50056")
    
    # Block until termination
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
