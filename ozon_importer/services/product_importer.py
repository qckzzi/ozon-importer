import asyncio
from collections.abc import Coroutine

from ozon_importer.exceptions import ProductTypeNotFoundError
from ozon_importer.interfaces import ILogger
from ozon_importer.services.interfaces import (
    IClient,
    IImageFetcher,
)
from ozon_importer.services.types import Characteristic, Product


class ProductImporter:
    def __init__(
        self,
        client: IClient,
        image_fetcher: IImageFetcher,
        marketplace_id: int,
    ) -> None:
        self.client: IClient = client
        self.image_fetcher: IImageFetcher = image_fetcher
        self.marketplace_id: int = marketplace_id

    async def send(self, product: Product, logger: ILogger | None = None) -> None:
        product_type_characteristic: Characteristic

        for characteristic in product.characteristics:
            if characteristic.name == "Тип":
                product_type_characteristic = characteristic
                product.characteristics.remove(characteristic)
                break
        else:
            raise ProductTypeNotFoundError(product.name)

        await self.client.send_category(
            {"name": product_type_characteristic.value, "marketplace_id": self.marketplace_id},
            logger,
        )
        await self.client.send_brand({"name": product.brand, "marketplace_id": self.marketplace_id}, logger)

        characteristic_tasks: list[Coroutine] = []
        characteristic_value_tasks: list[Coroutine] = []

        sended_characteristic_names: set[str] = set()

        for characteristic in product.characteristics:
            if characteristic.name not in sended_characteristic_names:
                characteristic_tasks.append(
                    self.client.send_characteristic(
                        {
                            "name": characteristic.name,
                            "product_type_name": product_type_characteristic.value,
                            "marketplace_id": self.marketplace_id,
                        },
                        logger,
                    ),
                )

                sended_characteristic_names.add(characteristic.name)

            characteristic_value_tasks.append(
                self.client.send_characteristic_value(
                    {
                        "value": characteristic.value,
                        "characteristic_name": characteristic.name,
                        "marketplace_id": self.marketplace_id,
                    },
                    logger,
                ),
            )

        await asyncio.gather(*characteristic_tasks)
        await asyncio.gather(*characteristic_value_tasks)

        product_id, is_new = await self.client.send_product(
            {
                "brand_name": product.brand,
                "characteristics": [{"name": ch.name, "value": ch.value} for ch in product.characteristics],
                "description": product.description,
                "external_id": int(product.sku),
                "marketplace_id": self.marketplace_id,
                "name": product.name,
                "url": product.url.unicode_string(),
                "category_name": product_type_characteristic.value,
            },
            logger,
        )

        if is_new:
            images: list[bytes] = await asyncio.gather(
                *[self.image_fetcher.fetch(url.unicode_string(), logger) for url in product.images],
            )

            await asyncio.gather(
                *[self.client.send_image({"body": image, "product_id": product_id}, logger) for image in images],
            )
