from tortoise.fields import *
from tortoise.models import Model

HASH_SIZE = 64

class FileModel(Model):
    hash: str = CharField(HASH_SIZE)
    size: int = IntField()
    type: str = CharField(max_length=255)
    names: ForeignKeyRelation["FilenameModel"]

class FilenameModel(Model):
    hash: str = CharField(HASH_SIZE) # File hash + name hash
    name: str = CharField(max_length=255)
    file: FileModel = ForeignKeyField("uploader.FileModel", related_name="names")