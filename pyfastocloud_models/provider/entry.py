from datetime import datetime
from enum import IntEnum

from pymodm import MongoModel, fields
from pymongo.operations import IndexModel
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

from pyfastocloud_models.service.entry import ServiceSettings
from pyfastocloud_models.load_balance.entry import LoadBalanceSettings
import pyfastocloud_models.constants as constants


class Provider(MongoModel):
    @staticmethod
    def get_by_id(sid: ObjectId):
        try:
            provider = Provider.objects.get({'_id': sid})
        except Provider.DoesNotExist:
            return None
        else:
            return provider

    @staticmethod
    def get_by_email(email: str):
        try:
            provider = Provider.objects.get({'email': email})
        except Provider.DoesNotExist:
            return None
        else:
            return provider

    class Status(IntEnum):
        NO_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

    class Type(IntEnum):
        GUEST = 0,
        USER = 1

    class Meta:
        collection_name = 'providers'
        allow_inheritance = True
        indexes = [IndexModel([('email', 1)], unique=True)]

    email = fields.EmailField(required=True)
    password = fields.CharField(required=True)
    created_date = fields.DateTimeField(default=datetime.now)
    status = fields.IntegerField(default=Status.NO_ACTIVE)
    type = fields.IntegerField(default=Type.USER)
    country = fields.CharField(min_length=2, max_length=3, required=True)
    language = fields.CharField(default=constants.DEFAULT_LOCALE, required=True)

    servers = fields.ListField(fields.ReferenceField(ServiceSettings, on_delete=fields.ReferenceField.PULL), default=[])
    load_balancers = fields.ListField(fields.ReferenceField(LoadBalanceSettings, on_delete=fields.ReferenceField.PULL),
                                      default=[])

    def get_id(self) -> str:
        return str(self.pk)

    @property
    def id(self):
        return self.pk

    def add_server(self, server):
        if server:
            self.servers.append(server)

    def remove_server(self, server):
        if server:
            self.servers.remove(server)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return generate_password_hash(password, method='sha256')

    @staticmethod
    def check_password_hash(hash_str: str, password: str) -> bool:
        return check_password_hash(hash_str, password)

    @classmethod
    def make_provider(cls, email: str, password: str, country: str, language: str):
        return cls(email=email, password=Provider.generate_password_hash(password), country=country, language=language)
