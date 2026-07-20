from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from db.schema import Base
import uuid

#roles - manager, buyer, manager with root permission

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(14), nullable = False, unique=True)
    email = Column(String(12), nullable = False, unique=True)
    password = Column(String(32), nullable = False)
    role = Column(String(12), default='buyer', nullable = False)
    date_created = Column(String, default=datetime.now(timezone.utc).strftime("%Y-%m-%d"), nullable = False)
    active = Column(Boolean, default=True)
    root = Column(Boolean, default=False)

    def __str__(self) -> str:
        return f"{self.id};{self.root};{self.username};{self.email};{self.password};{self.role};{self.date_created};{self.active}"
    
    def as_dict(self) -> dict:
        return {"id": str(self.id), "username": self.username, "email": self.email, "password": self.password, "role": self.role,
                "date_created": self.date_created, "active": self.active, "root": self.root}
