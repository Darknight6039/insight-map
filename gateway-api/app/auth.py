"""
Authentication module for Insight MVP
Handles user management, JWT tokens, and invitations
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from typing import List

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://insight_user:insight_password_2024@postgres:5432/insight_db")
# Prioritize Supabase JWT secret for token validation
SECRET_KEY = os.environ.get("SUPABASE_JWT_SECRET") or os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing - using bcrypt with explicit configuration to avoid version issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

# Security
security = HTTPBearer()


# =============================================================================
# DATABASE MODELS
# =============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user")  # "admin" or "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    invitations_sent = relationship("Invitation", back_populates="created_by_user", foreign_keys="Invitation.created_by")


class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)  # Optional: restrict to specific email
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", back_populates="invitations_sent", foreign_keys=[created_by])


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")


class ActivityLog(Base):
    """Log des activités utilisateur pour le monitoring admin"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # "login", "report_created", "chat", "search", etc.
    resource_type = Column(String, nullable=True)  # "report", "document", "watch"
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    invitation_code: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class InvitationCreate(BaseModel):
    email: Optional[EmailStr] = None
    expires_in_days: int = 7


class InvitationResponse(BaseModel):
    id: int
    code: str
    email: Optional[str]
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class PasswordResetTokenResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime]
    token: Optional[str] = None  # Only shown to admin
    
    class Config:
        from_attributes = True


# Activity log schemas
class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_reports: int
    total_logins_today: int
    total_logins_week: int
    total_activities_today: int
    reports_today: int
    reports_week: int
    total_watches: int
    watches_created_week: int
    watches_triggered_week: int


class ActivityChartData(BaseModel):
    date: str
    logins: int
    reports: int
    chats: int
    searches: int
    watches: int


class ReportTypeStats(BaseModel):
    type: str
    count: int


class DashboardCharts(BaseModel):
    activity_by_day: List[ActivityChartData]
    reports_by_type: List[ReportTypeStats]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def generate_invitation_code() -> str:
    """Generate a unique invitation code"""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a unique password reset token"""
    return secrets.token_urlsafe(32)


def log_activity(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[str] = None
) -> ActivityLog:
    """Log a user activity"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        # Ensure user_id is an integer
        user_id = int(user_id)
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Token decode error: {e}")
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        print(f"Database query error: {e}")
        raise credentials_exception
        
    if user is None:
        print(f"User not found for id: {user_id}")
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis"
        )
    return current_user


# =============================================================================
# AUTH OPERATIONS
# =============================================================================

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, user_data: UserCreate, invitation: Invitation) -> User:
    """Create a new user"""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Mark invitation as used
    invitation.used_at = datetime.utcnow()
    invitation.used_by = user.id
    db.commit()
    
    return user


def validate_invitation(db: Session, code: str, email: Optional[str] = None) -> Invitation:
    """Validate an invitation code"""
    invitation = db.query(Invitation).filter(Invitation.code == code).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code d'invitation invalide"
        )
    
    if invitation.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a déjà été utilisée"
        )
    
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation a expiré"
        )
    
    if invitation.email and email and invitation.email.lower() != email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette invitation n'est pas valide pour cet email"
        )
    
    return invitation


def create_invitation(db: Session, admin_user: User, data: InvitationCreate) -> Invitation:
    """Create a new invitation"""
    invitation = Invitation(
        code=generate_invitation_code(),
        email=data.email,
        created_by=admin_user.id,
        expires_at=datetime.utcnow() + timedelta(days=data.expires_in_days)
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


# =============================================================================
# PASSWORD RESET OPERATIONS
# =============================================================================

def create_password_reset_token(db: Session, email: str) -> Optional[PasswordResetToken]:
    """Create a password reset token for a user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    # Invalidate any existing tokens for this user
    existing_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at == None
    ).all()
    for token in existing_tokens:
        token.used_at = datetime.utcnow()  # Mark as used
    
    # Create new token (expires in 1 hour)
    reset_token = PasswordResetToken(
        token=generate_reset_token(),
        user_id=user.id,
        email=user.email,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token


def validate_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Validate a password reset token"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()
    
    if not reset_token:
        return None
    
    if reset_token.used_at:
        return None
    
    if reset_token.expires_at < datetime.utcnow():
        return None
    
    return reset_token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using a valid token"""
    reset_token = validate_reset_token(db, token)
    if not reset_token:
        return False
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        return False
    
    # Update password
    user.password_hash = get_password_hash(new_password)
    
    # Mark token as used
    reset_token.used_at = datetime.utcnow()
    
    db.commit()
    return True


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """Change user password (requires current password)"""
    if not verify_password(current_password, user.password_hash):
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    return True


# =============================================================================
# INITIALIZE DATABASE
# =============================================================================

def init_db():
    """Initialize database tables and create default admin if needed"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            # Create default admin user
            default_admin = User(
                email=os.environ.get("ADMIN_EMAIL", "admin@axial.com"),
                password_hash=get_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123")),
                full_name="Administrateur",
                role="admin"
            )
            db.add(default_admin)
            db.commit()
            print(f"Default admin created: {default_admin.email}")
    finally:
        db.close()

