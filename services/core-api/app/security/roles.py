import enum
from typing import List


class UserRole(str, enum.Enum):
    CONSUMER = "Consumer"
    INSPECTOR = "Inspector"
    SUPERVISOR = "Supervisor"
    ADMIN = "Admin"
    BRAND = "Brand"


ROLE_HIERARCHY = {
    UserRole.ADMIN: [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.INSPECTOR, UserRole.CONSUMER, UserRole.BRAND],
    UserRole.SUPERVISOR: [UserRole.SUPERVISOR, UserRole.INSPECTOR, UserRole.CONSUMER],
    UserRole.INSPECTOR: [UserRole.INSPECTOR, UserRole.CONSUMER],
    UserRole.CONSUMER: [UserRole.CONSUMER],
    UserRole.BRAND: [UserRole.BRAND],
}
