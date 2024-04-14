from typing import Final

from faststream import Logger

from ozon_importer.handlers.interfaces import IProductSender
from ozon_importer.handlers.types import Product


class ParsedLoadingHandler:
    def __init__(self, product_sender: IProductSender) -> None:
        self.product_sender: Final[IProductSender] = product_sender

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]"

    async def __call__(
        self,
        product: Product,
        logger: Logger,
    ) -> None:
        logger.debug(f"{self} received '{product.name}'")
        await self.product_sender.send(product, logger)  # type: ignore[arg-type]
