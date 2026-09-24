from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import Boolean,DateTime,ForeignKey,Integer,String,Text,UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB,UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .db import Base

def utcnow(): return datetime.now(timezone.utc)

class Manager(Base):
 __tablename__='managers'
 id:Mapped[str]=mapped_column(UUID(as_uuid=False),primary_key=True,default=lambda:str(uuid4()))
 username:Mapped[str]=mapped_column(String(64),unique=True,index=True)
 password_hash:Mapped[str]=mapped_column(String(255))
 is_active:Mapped[bool]=mapped_column(Boolean,default=True)
 applications:Mapped[list['Application']]=relationship(back_populates='manager')
 audit_logs:Mapped[list['AuditLog']]=relationship(back_populates='actor')

class Application(Base):
 __tablename__='applications'
 id:Mapped[str]=mapped_column(UUID(as_uuid=False),primary_key=True,default=lambda:str(uuid4()))
 application_number:Mapped[str]=mapped_column(String(32),unique=True,index=True)
 status:Mapped[str]=mapped_column(String(32),default='NEW',index=True)
 public_token_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
 login:Mapped[str]=mapped_column(String(255));lk_password_encrypted:Mapped[str]=mapped_column(Text)
 inn:Mapped[str]=mapped_column(String(14),index=True);company:Mapped[str]=mapped_column(String(255));legal_address:Mapped[str]=mapped_column(Text)
 director:Mapped[str]=mapped_column(String(255));director_inn:Mapped[str]=mapped_column(String(14));director_phone:Mapped[str]=mapped_column(String(32));director_email:Mapped[str]=mapped_column(String(255));extra_phone:Mapped[str]=mapped_column(String(32));extra_name:Mapped[str|None]=mapped_column(String(255),nullable=True)
 object_type:Mapped[str]=mapped_column(Text);activity:Mapped[str]=mapped_column(Text);ugns:Mapped[str]=mapped_column(String(255));place_type:Mapped[str]=mapped_column(String(64));point_name:Mapped[str]=mapped_column(String(255));point_address:Mapped[str]=mapped_column(Text);tax_regime:Mapped[str]=mapped_column(Text);vat:Mapped[bool]=mapped_column(Boolean,default=False);calc_types:Mapped[list]=mapped_column(JSONB);comment:Mapped[str|None]=mapped_column(Text,nullable=True);manager_id:Mapped[str|None]=mapped_column(UUID(as_uuid=False),ForeignKey('managers.id'),nullable=True,index=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,index=True);updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,onupdate=utcnow)
 manager:Mapped[Manager|None]=relationship(back_populates='applications');documents:Mapped[list['Document']]=relationship(back_populates='application',cascade='all, delete-orphan');audit_logs:Mapped[list['AuditLog']]=relationship(back_populates='application',cascade='all, delete-orphan')

class Document(Base):
 __tablename__='documents';__table_args__=(UniqueConstraint('application_id','document_type',name='uq_application_document_type'),)
 id:Mapped[str]=mapped_column(UUID(as_uuid=False),primary_key=True,default=lambda:str(uuid4()));application_id:Mapped[str]=mapped_column(UUID(as_uuid=False),ForeignKey('applications.id',ondelete='CASCADE'),index=True);document_type:Mapped[str]=mapped_column(String(32));original_name:Mapped[str]=mapped_column(String(255));storage_name:Mapped[str]=mapped_column(String(255),unique=True);mime_type:Mapped[str]=mapped_column(String(100));size_bytes:Mapped[int]=mapped_column(Integer);sha256:Mapped[str]=mapped_column(String(64),index=True);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow);application:Mapped[Application]=relationship(back_populates='documents')

class AuditLog(Base):
 __tablename__='audit_logs'
 id:Mapped[str]=mapped_column(UUID(as_uuid=False),primary_key=True,default=lambda:str(uuid4()));application_id:Mapped[str]=mapped_column(UUID(as_uuid=False),ForeignKey('applications.id',ondelete='CASCADE'),index=True);actor_manager_id:Mapped[str|None]=mapped_column(UUID(as_uuid=False),ForeignKey('managers.id'),nullable=True);action:Mapped[str]=mapped_column(String(64));details:Mapped[dict]=mapped_column(JSONB,default=dict);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,index=True);application:Mapped[Application]=relationship(back_populates='audit_logs');actor:Mapped[Manager|None]=relationship(back_populates='audit_logs')
