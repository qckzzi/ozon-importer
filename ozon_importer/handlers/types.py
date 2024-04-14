from pydantic import AnyHttpUrl, BaseModel


class Characteristic(BaseModel):
    name: str
    value: str


class Product(BaseModel):
    sku: str
    name: str
    brand: str
    description: str
    characteristics: list[Characteristic]
    images: list[AnyHttpUrl]
    url: AnyHttpUrl
