from dataclasses import dataclass


@dataclass
class User:

    ROLE_ADMIN = 'admin'
    ROLE_CLIENT = 'client'

    GENDER_MALE = "M"
    GENDER_FEMALE = "F"

    id: str
    name: str
    email: str
    password: str
    gender: str
    role: str
    phonenumber: str
