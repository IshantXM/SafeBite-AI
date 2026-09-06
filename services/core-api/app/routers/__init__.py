from app.routers.inspections import router as inspections_router
from app.routers.analytics import router as analytics_router
from app.routers.rules import router as rules_router
from app.routers.auth import router as auth_router

__all__ = ["inspections_router", "analytics_router", "rules_router", "auth_router"]
