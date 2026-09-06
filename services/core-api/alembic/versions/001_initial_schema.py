"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Create ENUM types safely
    op.execute("DO $$ BEGIN CREATE TYPE inspection_status_enum AS ENUM ('PENDING', 'COMPLIANT', 'FLAGGED', 'NOTICE_ISSUED'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE panel_type_enum AS ENUM ('FRONT', 'BACK', 'SIDE', 'TOP', 'BOTTOM'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE violation_severity_enum AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE violation_status_enum AS ENUM ('ACTIVE', 'RESOLVED', 'APPEALED'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Table: inspections
    op.create_table(
        'inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('barcode', sa.String(32), nullable=True),
        sa.Column('brand_name', sa.String(128), nullable=True),
        sa.Column('category', sa.String(64), nullable=True),
        sa.Column('geo_lat', sa.Float(), nullable=True),
        sa.Column('geo_lng', sa.Float(), nullable=True),
        sa.Column('geo_point', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('status', postgresql.ENUM('PENDING', 'COMPLIANT', 'FLAGGED', 'NOTICE_ISSUED', name='inspection_status_enum', create_type=False), nullable=False),
        sa.Column('image_sha256', sa.String(64), nullable=False),
        sa.Column('sync_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_inspections_inspector_id', 'inspections', ['inspector_id'])
    op.create_index('ix_inspections_barcode', 'inspections', ['barcode'])
    op.create_index('ix_inspections_brand_name', 'inspections', ['brand_name'])
    op.create_index('ix_inspections_status', 'inspections', ['status'])
    op.create_index('ix_inspections_image_sha256', 'inspections', ['image_sha256'])
    op.execute("CREATE INDEX IF NOT EXISTS idx_inspections_geo_point ON inspections USING GIST (geo_point);")

    # Table: inspection_panels
    op.create_table(
        'inspection_panels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('panel_type', postgresql.ENUM('FRONT', 'BACK', 'SIDE', 'TOP', 'BOTTOM', name='panel_type_enum', create_type=False), nullable=False),
        sa.Column('raw_image_url', sa.Text(), nullable=False),
        sa.Column('processed_image_url', sa.Text(), nullable=True),
        sa.Column('calibration_ratio_px_mm', sa.Float(), nullable=True),
    )
    op.create_index('ix_inspection_panels_inspection_id', 'inspection_panels', ['inspection_id'])

    # Table: detected_fields
    op.create_table(
        'detected_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('panel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspection_panels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_key', sa.String(64), nullable=False),
        sa.Column('extracted_value', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('bbox_coordinates', postgresql.JSONB(), nullable=True),
        sa.Column('measured_font_height_mm', sa.Float(), nullable=True),
        sa.Column('contrast_ratio', sa.Float(), nullable=True),
    )
    op.create_index('ix_detected_fields_panel_id', 'detected_fields', ['panel_id'])
    op.create_index('ix_detected_fields_field_key', 'detected_fields', ['field_key'])

    # Table: violations
    op.create_table(
        'violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_id', sa.String(64), nullable=False),
        sa.Column('clause_reference', sa.String(64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', postgresql.ENUM('CRITICAL', 'HIGH', 'MEDIUM', name='violation_severity_enum', create_type=False), nullable=False),
        sa.Column('ai_detected', sa.Boolean(), default=True, nullable=False),
        sa.Column('human_override', sa.Boolean(), default=False, nullable=False),
        sa.Column('penalty_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'RESOLVED', 'APPEALED', name='violation_status_enum', create_type=False), nullable=False),
        sa.Column('override_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_violations_inspection_id', 'violations', ['inspection_id'])
    op.create_index('ix_violations_rule_id', 'violations', ['rule_id'])
    op.create_index('ix_violations_status', 'violations', ['status'])

    # Table: rule_configurations
    op.create_table(
        'rule_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rule_set_name', sa.String(128), nullable=False),
        sa.Column('version', sa.String(16), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('rules_payload', postgresql.JSONB(), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_rule_configurations_is_active', 'rule_configurations', ['is_active'])

    # Table: audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('entity_type', sa.String(64), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('executed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payload_diff', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_executed_by', 'audit_logs', ['executed_by'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('rule_configurations')
    op.drop_table('violations')
    op.drop_table('detected_fields')
    op.drop_table('inspection_panels')
    op.drop_table('inspections')
    op.execute("DROP TYPE IF EXISTS violation_status_enum")
    op.execute("DROP TYPE IF EXISTS violation_severity_enum")
    op.execute("DROP TYPE IF EXISTS panel_type_enum")
    op.execute("DROP TYPE IF EXISTS inspection_status_enum")
