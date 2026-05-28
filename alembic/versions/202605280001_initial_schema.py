"""initial schema

Revision ID: 202605280001
Revises:
Create Date: 2026-05-28 00:01:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605280001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    user_role = sa.Enum("ADMINISTRADOR", "OPERADOR", name="user_role")
    movement_type = sa.Enum("ENTRADA", "SAIDA", "AJUSTE", name="movement_type")
    user_role.create(op.get_bind(), checkfirst=True)
    movement_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("minimum_stock", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("sku", name=op.f("uq_products_sku")),
    )
    op.create_index(op.f("ix_products_category"), "products", ["category"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=False)

    op.create_table(
        "movements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("movement_type", movement_type, nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("observation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name=op.f("fk_movements_product_id_products")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_movements_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_movements")),
    )
    op.create_index(op.f("ix_movements_created_at"), "movements", ["created_at"], unique=False)
    op.create_index(op.f("ix_movements_product_id"), "movements", ["product_id"], unique=False)
    op.create_index(op.f("ix_movements_user_id"), "movements", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_movements_user_id"), table_name="movements")
    op.drop_index(op.f("ix_movements_product_id"), table_name="movements")
    op.drop_index(op.f("ix_movements_created_at"), table_name="movements")
    op.drop_table("movements")
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_category"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    sa.Enum(name="movement_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=True)
