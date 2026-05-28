"""expand products with new fields and models

Revision ID: 202605280002
Revises: 202605280001
Create Date: 2026-05-28 00:02:00
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605280002"
down_revision: str | None = "202605280001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "brands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_brands")),
        sa.UniqueConstraint("name", name=op.f("uq_brands_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_brands_slug")),
    )

    op.create_table(
        "suppliers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=True),
        sa.Column("contact_name", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_suppliers")),
        sa.UniqueConstraint("cnpj", name=op.f("uq_suppliers_cnpj")),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("slug", name=op.f("uq_categories_slug")),
    )
    op.create_index(op.f("ix_categories_parent_id"), "categories", ["parent_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_categories_parent_id_categories"),
        "categories", "categories",
        ["parent_id"], ["id"],
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=False),
        sa.Column("slug", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_tags_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_tags_slug")),
    )

    op.create_table(
        "product_tags",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_product_tags_product_id_products")),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name=op.f("fk_product_tags_tag_id_tags")),
        sa.PrimaryKeyConstraint("product_id", "tag_id", name=op.f("pk_product_tags")),
    )

    op.create_table(
        "product_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("alt", sa.String(length=200), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_product_images_product_id_products")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_images")),
    )
    op.create_index(op.f("ix_product_images_product_id"), "product_images", ["product_id"], unique=False)

    op.create_table(
        "product_reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name=op.f("ck_product_reviews_rating_range")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_product_reviews_product_id_products")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_product_reviews_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_reviews")),
    )
    op.create_index(op.f("ix_product_reviews_product_id"), "product_reviews", ["product_id"], unique=False)
    op.create_index(op.f("ix_product_reviews_user_id"), "product_reviews", ["user_id"], unique=False)

    op.create_table(
        "carts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_carts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carts")),
        sa.UniqueConstraint("user_id", name=op.f("uq_carts_user_id")),
    )
    op.create_index(op.f("ix_carts_user_id"), "carts", ["user_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], name=op.f("fk_cart_items_cart_id_carts")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name=op.f("fk_cart_items_product_id_products")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart_items")),
        sa.UniqueConstraint("cart_id", "product_id", name=op.f("uq_cart_items_cart_id_product_id")),
    )
    op.create_index(op.f("ix_cart_items_cart_id"), "cart_items", ["cart_id"], unique=False)
    op.create_index(op.f("ix_cart_items_product_id"), "cart_items", ["product_id"], unique=False)

    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(sa.Column("category_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("brand_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("supplier_id", sa.Uuid(), nullable=True))
        batch_op.add_column(sa.Column("ean", sa.String(length=13), nullable=True))
        batch_op.add_column(sa.Column("weight_g", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("height_cm", sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column("width_cm", sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column("depth_cm", sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.text("false")))
        batch_op.add_column(sa.Column("rating_avg", sa.Numeric(2, 1), nullable=False, server_default=sa.text("0")))
        batch_op.add_column(sa.Column("rating_count", sa.Integer(), nullable=False, server_default=sa.text("0")))
        batch_op.create_index(op.f("ix_products_category_id"), ["category_id"])
        batch_op.create_index(op.f("ix_products_brand_id"), ["brand_id"])
        batch_op.create_index(op.f("ix_products_supplier_id"), ["supplier_id"])
        batch_op.create_foreign_key(op.f("fk_products_category_id_categories"), "categories", ["category_id"], ["id"])
        batch_op.create_foreign_key(op.f("fk_products_brand_id_brands"), "brands", ["brand_id"], ["id"])
        batch_op.create_foreign_key(op.f("fk_products_supplier_id_suppliers"), "suppliers", ["supplier_id"], ["id"])
        batch_op.create_unique_constraint(op.f("uq_products_ean"), ["ean"])


def downgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint(op.f("uq_products_ean"), type_="unique")
        batch_op.drop_constraint(op.f("fk_products_supplier_id_suppliers"), type_="foreignkey")
        batch_op.drop_constraint(op.f("fk_products_brand_id_brands"), type_="foreignkey")
        batch_op.drop_constraint(op.f("fk_products_category_id_categories"), type_="foreignkey")
        batch_op.drop_index(op.f("ix_products_supplier_id"))
        batch_op.drop_index(op.f("ix_products_brand_id"))
        batch_op.drop_index(op.f("ix_products_category_id"))
        batch_op.drop_column("rating_count")
        batch_op.drop_column("rating_avg")
        batch_op.drop_column("featured")
        batch_op.drop_column("depth_cm")
        batch_op.drop_column("width_cm")
        batch_op.drop_column("height_cm")
        batch_op.drop_column("weight_g")
        batch_op.drop_column("ean")
        batch_op.drop_column("supplier_id")
        batch_op.drop_column("brand_id")
        batch_op.drop_column("category_id")

    op.drop_table("cart_items")
    op.drop_index(op.f("ix_cart_items_product_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_cart_id"), table_name="cart_items")
    op.drop_table("carts")
    op.drop_index(op.f("ix_carts_user_id"), table_name="carts")
    op.drop_table("product_reviews")
    op.drop_index(op.f("ix_product_reviews_user_id"), table_name="product_reviews")
    op.drop_index(op.f("ix_product_reviews_product_id"), table_name="product_reviews")
    op.drop_table("product_images")
    op.drop_index(op.f("ix_product_images_product_id"), table_name="product_images")
    op.drop_table("product_tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_categories_parent_id"), table_name="categories")
    op.drop_constraint(op.f("fk_categories_parent_id_categories"), "categories", type_="foreignkey")
    op.drop_table("categories")
    op.drop_table("suppliers")
    op.drop_table("brands")
