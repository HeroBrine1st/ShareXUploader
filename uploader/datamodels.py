from typing import List
from pydantic import BaseModel
from uploader.models import FileModel


class FileDataModel(BaseModel):
    hash: str
    type: str
    size: int
    names: List[str]
    # TODO uploader

    @staticmethod
    async def of(model: FileModel):
        await model.fetch_related("names")
        return FileDataModel(hash=model.hash,
                             type=model.type,
                             size=model.size,
                             names=[name.name for name in model.names])
