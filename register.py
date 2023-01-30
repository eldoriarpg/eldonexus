import os
import random
import string

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth


class ContentSelector(BaseModel):
    name: str
    description: str
    expression: str


class Role(BaseModel):
    id: str
    name: str
    description: str
    privileges: list[str]
    roles: list[str]


class User(BaseModel):
    userId: str
    firstName: str
    lastName: str
    emailAddress: str
    password: str
    status: str = "active"
    roles: list[str]


class RepositoryContentSelector(BaseModel):
    name: str
    description: str
    actions: list[str]
    format: str = None
    repository: str
    contentSelector: str


load_dotenv()

base_url = os.environ["nexus_url"] + "/service/rest/"
base_roles = os.environ["base_roles"].split(",")

domains = input("Please enter the required group ids tld.domain.sub space seperated:\n").split(" ")
base_domain = domains[0]
description = ", ".join(domains)
firstName = input("First name:\n")
lastName = input("Last Name:\n")
mail = input("Mail:\n") or base_domain + "@eldonexus.de"

session = requests.Session()
session.auth = HTTPBasicAuth(os.environ['nexus_user'], os.environ['nexus_password'])


def post(url: str, data: BaseModel):
    response = session.post(f"{base_url}{url}", json=data.dict(),
                            headers={"Content-Type": "application/json",
                                     "accept": "application/json"})
    response.raise_for_status()


# Create selectors
select = " or ".join([f"path =^ \"/{e.replace('.', '/')}\"" for e in domains])
select = f'format == "maven2" and ({select})'

print("Creating selector")
post("v1/security/content-selectors", ContentSelector(name=base_domain, description=description, expression=select))

privilege = RepositoryContentSelector(name=base_domain, description=description, actions=["ALL"], repository="*",
                                      contentSelector=base_domain, format="maven2")

print("Creating content selector privilege")
post("v1/security/privileges/repository-content-selector", privilege)

print("Creating role")
post("v1/security/roles",
     Role(id=base_domain, name=base_domain, description=description, privileges=[base_domain], roles=base_roles))

user = User(userId=base_domain, firstName=firstName, lastName=lastName, emailAddress=mail, status="active",
            password=''.join(random.choice(string.ascii_lowercase) for i in range(20)), roles=[base_domain])

print("Creating user")
post("v1/security/users", user)

print("User created.")
print(f"Id: {user.userId}")
print(f"Password: {user.password}")
print(f"Active domains: {', '.join(domains)}")
