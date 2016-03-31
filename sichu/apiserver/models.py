from django.contrib.auth.models import User
from django.db import models
from enum import Enum


OP_ADD    = 1
OP_UPDATE = 2
OP_DELETE = 3


class DjEnum(Enum):

    @classmethod
    def choices(cls):
        choices = []
        for i in cls:
            choices.append((i.value, i.name))
        return tuple(choices)


class OperationLog(models.Model):
    timestamp = models.IntegerField()
    users     = models.ManyToManyField(User)
    opcode    = models.PositiveSmallIntegerField()
    model     = models.CharField(max_length=64)
    data      = models.TextField()


class GexinID(models.Model):
    client_id = models.CharField(max_length=32)
    user      = models.ForeignKey(User)


class ExportStatus(DjEnum):
    idel = 1
    succeed = 2
    failed = 3


class ExportLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email      = models.EmailField()
    status     = models.IntegerField(choices=ExportStatus.choices(),
                                     default=ExportStatus.idel.value)
    user       = models.ForeignKey(User)


class EmailVerify(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email      = models.EmailField()
    code       = models.CharField(max_length=32, unique=True)
    verified   = models.BooleanField()
    user       = models.ForeignKey(User)
