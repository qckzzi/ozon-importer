from typing import TypedDict


class ProductCharacteristic(TypedDict):
    name: str
    value: str


class Product(TypedDict):
    external_id: int
    name: str
    url: str
    category_name: str
    brand_name: str
    marketplace_id: int
    description: str
    characteristics: list[ProductCharacteristic]


class Category(TypedDict):
    name: str
    marketplace_id: int


class Brand(TypedDict):
    name: str
    marketplace_id: int


class Characteristic(TypedDict):
    name: str
    marketplace_id: int


class CharacteristicValue(TypedDict):
    value: str
    characteristic_name: str
    marketplace_id: int


class Image(TypedDict):
    body: bytes
    product_id: int
