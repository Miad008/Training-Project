from enum import Enum

from pydantic import BaseModel, EmailStr


# =========================================================
# User Role
# =========================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    TRAINEE = "trainee"


# =========================================================
# User Status
# =========================================================

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# =========================================================
# Create User
# =========================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


# =========================================================
# Update User
# =========================================================

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    status: UserStatus | None = None


# =========================================================
# User Response
# =========================================================

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus