from collections.abc import Sequence
from typing import Protocol

from pydantic import AnyHttpUrl

from ozon_importer.interfaces import ILogger


class ICharacteristic(Protocol):
    name: str
    value: str


class IProduct(Protocol):
    sku: str
    name: str
    brand: str
    description: str
    characteristics: Sequence[ICharacteristic]
    images: Sequence[AnyHttpUrl]
    url: AnyHttpUrl


class IProductSender(Protocol):
    async def send(self, product: IProduct, logger: ILogger | None = None) -> None: ...
