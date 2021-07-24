from pydantic import BaseModel


class AddData(BaseModel):
    a: float
    b: float
