from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from db.schema import Base
import uuid


class ClientModel(Base):
    __tablename__ = 'clients'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(24),default='User did not provide data', nullable=False)
    email = Column(String(64), default='User did not provide data', nullable=False)
    message = Column(String(255), default='User did not provide data', nullable=False)
    phone_number = Column(String(26), default='User did not provide data', nullable=False)
    date_created = Column(String(), default = datetime.now(timezone.utc).strftime("%Y-%m-%d"), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    date_completed = Column(String(30), default="Isn't provided", nullable=False)

    def __str__(self):
        return f"{self.id};{self.full_name};{self.email};{self.message};{self.phone_number};{self.date_created};"
    
    def as_dict(self):
        return {"id": self.id, "full_name": self.full_name, "email": self.email, "message": self.message, "phone_number": self.phone_number,
                "date_created": self.date_created}
