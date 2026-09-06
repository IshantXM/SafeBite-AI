from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.inspection import Inspection, InspectionStatus
from app.models.violation import Violation, ViolationStatus
from app.schemas.analytics import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    RepeatOffenderItem,
    RepeatOffendersResponse,
)
from app.security.auth import AuthUser, get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Provides high-level dashboard KPIs for Command Center."""
    # Total inspections
    total_inspections = await db.scalar(select(func.count(Inspection.id))) or 0

    # Status counts
    flagged_count = await db.scalar(select(func.count(Inspection.id)).where(Inspection.status == InspectionStatus.FLAGGED)) or 0
    notice_issued_count = await db.scalar(select(func.count(Inspection.id)).where(Inspection.status == InspectionStatus.NOTICE_ISSUED)) or 0
    compliant_count = await db.scalar(select(func.count(Inspection.id)).where(Inspection.status == InspectionStatus.COMPLIANT)) or 0
    pending_count = await db.scalar(select(func.count(Inspection.id)).where(Inspection.status == InspectionStatus.PENDING)) or 0

    # Total penalties assessed
    total_penalties = await db.scalar(
        select(func.sum(Violation.penalty_amount)).where(Violation.status == ViolationStatus.ACTIVE)
    ) or 0

    # Violation rate calculation
    reviewed_total = flagged_count + notice_issued_count + compliant_count
    violation_rate = round(((flagged_count + notice_issued_count) / reviewed_total * 100), 1) if reviewed_total > 0 else 0.0

    return {
        "total_inspections": total_inspections,
        "pending_reviews": pending_count,
        "flagged_cases": flagged_count,
        "notices_issued": notice_issued_count,
        "compliant_cases": compliant_count,
        "violation_rate_pct": violation_rate,
        "total_penalties_assessed_inr": float(total_penalties)
    }


@router.get("/heatmaps", response_model=GeoJSONFeatureCollection)
async def get_violation_heatmaps(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Returns PostGIS GeoJSON feature collection of inspection violations across regions."""
    query = select(Inspection).where(
        Inspection.geo_lat.isnot(None),
        Inspection.geo_lng.isnot(None)
    ).limit(1000)

    result = await db.execute(query)
    inspections = result.scalars().all()

    features: List[GeoJSONFeature] = []
    for insp in inspections:
        features.append(GeoJSONFeature(
            type="Feature",
            geometry=GeoJSONGeometry(
                type="Point",
                coordinates=[insp.geo_lng, insp.geo_lat]
            ),
            properties={
                "id": str(insp.id),
                "brand_name": insp.brand_name or "Unknown Brand",
                "category": insp.category or "General",
                "status": insp.status.value,
                "violation_count": len(insp.violations),
                "sync_timestamp": insp.sync_timestamp.isoformat(),
            }
        ))

    return GeoJSONFeatureCollection(type="FeatureCollection", features=features)


@router.get("/repeat-offenders", response_model=RepeatOffendersResponse)
async def get_repeat_offenders(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user)
):
    """Identifies recurring non-compliant brands/manufacturers with cumulative penalties."""
    query = (
        select(
            Inspection.brand_name,
            Inspection.category,
            func.count(Violation.id).label("violation_count"),
            func.sum(Violation.penalty_amount).label("total_penalties")
        )
        .join(Violation, Violation.inspection_id == Inspection.id)
        .where(Inspection.brand_name.isnot(None))
        .group_by(Inspection.brand_name, Inspection.category)
        .order_by(desc("violation_count"))
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    offenders = []
    for row in rows:
        offenders.append(RepeatOffenderItem(
            brand_name=row.brand_name,
            category=row.category or "Packaged Commodity",
            violation_count=row.violation_count,
            total_penalties_inr=float(row.total_penalties or 0),
            common_violations=["Rule 6(1)(c) - Missing Tax Phrase", "Rule 7 - Font Height Below Threshold"]
        ))

    return RepeatOffendersResponse(total_offenders=len(offenders), offenders=offenders)
