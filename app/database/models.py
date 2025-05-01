from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Enum as SAEnum,
    Text,
    DateTime,
    Float,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Date,
    Time,
    Boolean,
    Numeric,
)
from sqlalchemy.orm import relationship, declarative_base

from app.database.types import (
    UserType,
    ProviderType,
    RecordType,
    AnimalType,
    DocumentType,
    DocumentStatus,
    BookingStatus,
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(80))
    surname = Column(String(80))
    patronymic = Column(String(80))
    role = Column(SAEnum(UserType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": UserType.user,
        "polymorphic_load": "inline",
    }
    owner = relationship("Owner", back_populates="user", uselist=False)
    provider = relationship("Provider", back_populates="user", uselist=False)

    def __repr__(self):
        return f"{self.surname} {self.first_name} {self.patronymic or ''}"


class Owner(User):
    __tablename__ = "owners"
    id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    phone = Column(String(20), unique=True)
    address = Column(String(200))

    pets = relationship(
        "Pet", back_populates="owner", cascade="all, delete-orphan"
    )
    __mapper_args__ = {
        "polymorphic_identity": UserType.owner,
    }

    user = relationship("User", back_populates="owner")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    base_price = Column(Numeric(10, 2))
    duration_min = Column(Integer)

    service_type = Column(SAEnum(ProviderType), nullable=False)
    provider_services = relationship(
        "ProviderService",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    providers = relationship(
        "Provider",
        secondary="provider_services",
        viewonly=True,
        back_populates="services",
    )

    __mapper_args__ = {"polymorphic_on": service_type, "with_polymorphic": "*"}


class VeterinaryService(Service):
    __tablename__ = "veterinary_services"
    id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), primary_key=True
    )
    animal_type = Column(String(50))
    emergency_available = Column(Boolean)

    __mapper_args__ = {"polymorphic_identity": ProviderType.vet}


class GroomingService(Service):
    __tablename__ = "grooming_services"
    id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), primary_key=True
    )
    tools_required = Column(String(200))
    coat_type = Column(String(50))

    __mapper_args__ = {"polymorphic_identity": ProviderType.groomer}


class SittingService(Service):
    __tablename__ = "sitting_services"
    id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), primary_key=True
    )
    max_pets = Column(Integer)
    overnight_available = Column(Boolean)

    __mapper_args__ = {"polymorphic_identity": ProviderType.sitter}


class Provider(User):
    __tablename__ = "providers"
    id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    company_name = Column(String(100))
    provider_type = Column(SAEnum(ProviderType), nullable=False)
    service_radius_km = Column(Integer, default=10)
    hourly_rate = Column(Float(precision=2))
    is_verified = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="provider")

    documents = relationship(
        "ProviderDocument",
        back_populates="provider",
        cascade="all, delete-orphan",
    )
    provider_services = relationship(
        "ProviderService",
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    services = relationship(
        "Service",
        secondary="provider_services",
        viewonly=True,
        back_populates="providers",
        lazy="selectin",
    )
    slots = relationship(
        "AvailableSlot",
        back_populates="provider",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __mapper_args__ = {
        "polymorphic_identity": UserType.provider,
    }


class ProviderService(Base):
    __tablename__ = "provider_services"
    __table_args__ = (
        UniqueConstraint(
            "provider_id", "service_id", name="uq_provider_service"
        ),
    )

    id = Column(Integer, primary_key=True)
    provider_id = Column(
        Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False
    )
    service_id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )

    custom_price = Column(Numeric(10, 2), nullable=False)
    custom_duration = Column(Integer, nullable=False)
    extra_info = Column(Text)

    provider = relationship("Provider", back_populates="provider_services")

    service = relationship("Service", back_populates="provider_services")


class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("owners.id", ondelete="CASCADE"))
    name = Column(String(50), nullable=False)
    animal_type = Column(SAEnum(AnimalType), nullable=False)
    breed = Column(String(50))
    birth_date = Column(Date)
    medical_notes = Column(Text)

    owner = relationship("Owner", back_populates="pets")

    medical_records = relationship(
        "MedicalRecord",
        back_populates="pet",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    booking = relationship("Booking", back_populates="pet")


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"))
    record_type = Column(SAEnum(RecordType), nullable=False)
    description = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    document_url = Column(String(200))

    pet = relationship("Pet", back_populates="medical_records")


class ProviderDocument(Base):
    __tablename__ = "provider_documents"
    __table_args__ = (
        UniqueConstraint(
            "provider_id", "document_type", name="uq_provider_doc_type"
        ),
    )
    id = Column(Integer, primary_key=True)
    provider_id = Column(
        Integer, ForeignKey("providers.id", ondelete="CASCADE")
    )
    document_type = Column(SAEnum(DocumentType), nullable=False)
    file_url = Column(String(200), nullable=False)
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.pending)

    provider = relationship("Provider", back_populates="documents")


class AvailableSlot(Base):
    __tablename__ = "available_slots"
    __table_args__ = (
        UniqueConstraint(
            "provider_id", "date", "start_time", name="uq_slot_provider_time"
        ),
    )

    id = Column(Integer, primary_key=True)
    provider_id = Column(
        Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)

    provider = relationship("Provider", back_populates="slots", lazy="selectin")
    bookings = relationship("Booking", back_populates="slot")


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("slot_id", "pet_id", name="uq_booking_slot_pet"),
        UniqueConstraint(
            "pet_id",
            "slot_id",
            "service_id",
            name="uq_booking_pet_slot_service",
        ),
    )

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("available_slots.id"))
    service_id = Column(ForeignKey("services.id"), nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.pending)
    notes = Column(Text, nullable=True)

    pet = relationship("Pet", back_populates="booking", lazy="selectin")
    slot = relationship(
        "AvailableSlot", back_populates="bookings", lazy="selectin"
    )
    service = relationship("Service", lazy="selectin")
