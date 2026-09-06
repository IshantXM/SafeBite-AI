import asyncio
import json
import os
import uuid
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.rule_config import RuleConfiguration


async def seed_initial_rules():
    """Reads rules/lm_rules_2011.json and seeds it into rule_configurations."""
    rules_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "rules", "lm_rules_2011.json")
    )
    if not os.path.exists(rules_file):
        rules_file = settings.RULES_JSON_PATH

    if not os.path.exists(rules_file):
        print(f"[ERROR] Statutory rules JSON not found at {rules_file}")
        return

    with open(rules_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RuleConfiguration).where(RuleConfiguration.version == payload.get("version", "2026.1"))
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"[INFO] Rule configuration v{existing.version} already exists. Updating payload...")
            existing.rules_payload = payload
            existing.is_active = True
        else:
            print(f"[INFO] Seeding Rule configuration v{payload.get('version')}...")
            new_rule = RuleConfiguration(
                id=uuid.uuid4(),
                rule_set_name=payload.get("rule_set_name", "Legal Metrology Rules 2011"),
                version=payload.get("version", "2026.1"),
                is_active=True,
                rules_payload=payload,
                updated_by=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            )
            session.add(new_rule)

        await session.commit()
        print("[SUCCESS] Statutory rules successfully seeded in PostgreSQL.")


if __name__ == "__main__":
    asyncio.run(seed_initial_rules())
