from enum import Enum, unique


@unique
class UserType(str, Enum):
    user = "user"
    owner = "owner"
    provider = "provider"
    admin = "admin"


@unique
class ProviderType(str, Enum):
    vet = "vet"
    groomer = "groomer"
    sitter = "sitter"


@unique
class AnimalType(str, Enum):
    dog = "dog"
    cat = "cat"


@unique
class RecordType(str, Enum):
    vaccine = "vaccine"
    diagnosis = "diagnosis"
    allergy = "allergy"


@unique
class DocumentType(str, Enum):
    license = "license"
    certificate = "certificate"


@unique
class DocumentStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


@unique
class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
