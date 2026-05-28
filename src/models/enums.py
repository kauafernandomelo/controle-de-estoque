from enum import StrEnum


class UserRole(StrEnum):
    """Available user roles."""

    ADMIN = "ADMINISTRADOR"
    OPERATOR = "OPERADOR"


class MovementType(StrEnum):
    """Supported stock movement types."""

    IN = "ENTRADA"
    OUT = "SAIDA"
    ADJUST = "AJUSTE"
