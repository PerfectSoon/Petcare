from .auth import router as users_router
from .booking import router as booking_router
from .service import router as service_router
from .owner.pet import router as pet_router
from .provider.slot import router as slot_router

__all__ = [
    "users_router",
    "booking_router",
    "service_router",
    "pet_router",
    "slot_router",
]
