"""
Database models for AEdificium Server
"""
import secrets
import string

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

ALPHABET = string.ascii_letters + string.digits


def generate_id(email):
    """
    Generate a RegisteredTeam id
    """
    return email + " " + "".join(secrets.choice(ALPHABET) for _ in range(16))


class RegistrationRequest(SQLModel):
    """
    Request to register a team
    """

    name: str = Field(unique=True)
    pl: str
    email: EmailStr


class RegistrationResponse(SQLModel):
    """
    Response for a successful registration
    """

    id: str = Field(primary_key=True)


class RegisteredTeam(RegistrationRequest, RegistrationResponse, table=True):
    """
    registeredteam table
    """
