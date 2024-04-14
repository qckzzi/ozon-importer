from typing import Protocol, TypedDict

from ozon_importer.interfaces import ILogger


class IProductCharacteristic(TypedDict):
    name: str
    value: str


class IProduct(TypedDict):
    external_id: int
    name: str
    url: str
    category_name: str
    brand_name: str
    marketplace_id: int
    description: str
    characteristics: list[IProductCharacteristic]


class IBrand(TypedDict):
    name: str
    marketplace_id: int


class ICategory(TypedDict):
    name: str
    marketplace_id: int


class ICharacteristic(TypedDict):
    name: str
    product_type_name: str
    marketplace_id: int


class ICharacteristicValue(TypedDict):
    value: str
    characteristic_name: str
    marketplace_id: int


class IImage(TypedDict):
    body: bytes
    product_id: int


class IClient(Protocol):
    async def send_product(self, product: IProduct, logger: ILogger | None = None) -> tuple[int, bool]: ...

    async def send_characteristic(
        self,
        characteristic: ICharacteristic,
        logger: ILogger | None = None,
    ) -> tuple[int, bool]: ...

    async def send_characteristic_value(
        self,
        characteristic_value: ICharacteristicValue,
        logger: ILogger | None = None,
    ) -> tuple[int, bool]: ...

    async def send_brand(self, brand: IBrand, logger: ILogger | None = None) -> tuple[int, bool]: ...

    async def send_category(self, brand: ICategory, logger: ILogger | None = None) -> tuple[int, bool]: ...

    async def send_image(self, image: IImage, logger: ILogger | None = None) -> tuple[int, bool]: ...


class IImageFetcher(Protocol):
    async def fetch(self, url: str, logger: ILogger | None = None) -> bytes: ...
