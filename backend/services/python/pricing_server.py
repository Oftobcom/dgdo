# pricing_server.py

import grpc
from concurrent import futures
import uuid
import threading
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from pricing_pb2_grpc import PricingServiceServicer, add_PricingServiceServicer_to_server
from pricing_pb2 import PriceCalculationRequest, PriceCalculationResponse, FallbackPricingConfig
from common_pb2 import Metadata

# -----------------------------
# In-memory fallback configuration
# -----------------------------
fallback_lock = threading.Lock()
fallback_config = FallbackPricingConfig(
    base_rate_kzt=300.0,
    per_meter_rate_kzt=0.05,
    per_second_rate_kzt=0.5,
    minimum_fare_kzt=500.0,
    platform_commission_rate=0.20,
    config_version="v1",
)

# -----------------------------
# Helpers
# -----------------------------
def now_timestamp():
    ts = Timestamp()
    ts.FromDatetime(datetime.utcnow())
    return ts

def positive_unit_economics(passenger_total, driver_payout, operational_cost=50):
    """
    Enforce positive unit economics:
    passenger > driver payout > operational cost
    """
    return passenger_total > driver_payout > operational_cost

# -----------------------------
# Pricing Service
# -----------------------------
class PricingService(PricingServiceServicer):

    def CalculatePrice(self, request: PriceCalculationRequest, context):
        with fallback_lock:
            cfg = fallback_config

        # Base components
        base = cfg.base_rate_kzt
        distance_fare = request.estimated_distance_meters * cfg.per_meter_rate_kzt
        time_fare = request.estimated_duration_seconds * cfg.per_second_rate_kzt
        surge = max(1.0, request.demand_multiplier)

        passenger_total = (base + distance_fare + time_fare) * surge
        if passenger_total < cfg.minimum_fare_kzt:
            passenger_total = cfg.minimum_fare_kzt

        commission = cfg.platform_commission_rate
        driver_payout = passenger_total * (1.0 - commission)
        platform_take = passenger_total - driver_payout

        # Enforce positive unit economics
        if not positive_unit_economics(passenger_total, driver_payout):
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("Unit economics violated: adjust pricing configuration")
            return PriceCalculationResponse()

        # Build response
        resp = PriceCalculationResponse(
            trip_request_id=request.trip_request_id,
            calculation_id=str(uuid.uuid4()),
            passenger_fare_total=passenger_total,
            driver_payout_total=driver_payout,
            platform_commission=platform_take,
            estimated_distance_meters=request.estimated_distance_meters,
            estimated_duration_seconds=request.estimated_duration_seconds,
            demand_multiplier_at_request=request.demand_multiplier,
            pricing_model_version="fallback_linear_v1",
            pricing_tier="economy",
            price_expires_at=now_timestamp(),
            calculated_at=now_timestamp(),
        )

        # Breakdown
        resp.passenger_breakdown.base_fare = base
        resp.passenger_breakdown.distance_fare = distance_fare
        resp.passenger_breakdown.time_fare = time_fare
        resp.passenger_breakdown.surge_multiplier = surge

        resp.driver_breakdown.base_fare = base * (1 - commission)
        resp.driver_breakdown.distance_fare = distance_fare * (1 - commission)
        resp.driver_breakdown.time_fare = time_fare * (1 - commission)
        resp.driver_breakdown.surge_multiplier = surge

        resp.calculation_metadata.data["pricing_model"] = resp.pricing_model_version
        print(f"[{datetime.utcnow()}] Calculated price for trip {request.trip_request_id}: {passenger_total}")
        return resp

    def GetFallbackConfig(self, request: FallbackPricingConfig, context):
        with fallback_lock:
            return fallback_config

    def UpdateFallbackConfig(self, request: FallbackPricingConfig, context):
        with fallback_lock:
            fallback_config.base_rate_kzt = request.base_rate_kzt
            fallback_config.per_meter_rate_kzt = request.per_meter_rate_kzt
            fallback_config.per_second_rate_kzt = request.per_second_rate_kzt
            fallback_config.minimum_fare_kzt = request.minimum_fare_kzt
            fallback_config.platform_commission_rate = request.platform_commission_rate
            fallback_config.config_version = request.config_version or fallback_config.config_version
        print(f"[{datetime.utcnow()}] Updated fallback config to version {fallback_config.config_version}")
        return fallback_config

def serve():
    """
    Start the gRPC server and listen for incoming pricing requests.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    # Register PricingService to gRPC server
    add_PricingServiceServicer_to_server(PricingService(), server)
    # Bind to port 50056
    server.add_insecure_port('[::]:50056')
    server.start()
    print("PricingService running on port 50056")
    # Block until termination
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
