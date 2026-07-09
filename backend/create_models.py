import os

models_dir = r"c:\Users\asire\OneDrive\Desktop\RevenuePulse\backend\app\models"

role_code = """from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Role(Base):
    __tablename__ = "saas_roles"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))

    users = relationship("User", secondary="saas_user_roles", back_populates="roles")
"""

user_role_code = """from sqlalchemy import Column, String, ForeignKey
from backend.app.database.database import Base

class UserRole(Base):
    __tablename__ = "saas_user_roles"

    user_id = Column(String(36), ForeignKey("saas_users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(36), ForeignKey("saas_roles.id", ondelete="CASCADE"), primary_key=True)
"""

audit_log_code = """from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class AuditLog(Base):
    __tablename__ = "saas_audit_logs"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("saas_users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
"""

notification_code = """from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from backend.app.database.database import Base

class Notification(Base):
    __tablename__ = "saas_notifications"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("saas_users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
"""

token_blacklist_code = """from sqlalchemy import Column, String, DateTime, func
from backend.app.database.database import Base

class TokenBlacklist(Base):
    __tablename__ = "saas_token_blacklist"

    token = Column(String(512), primary_key=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
"""

files = {
    "Role.py": role_code,
    "UserRole.py": user_role_code,
    "AuditLog.py": audit_log_code,
    "Notification.py": notification_code,
    "TokenBlacklist.py": token_blacklist_code
}

for fname, code in files.items():
    with open(os.path.join(models_dir, fname), "w") as f:
        f.write(code)

print("SAAS Models created.")
