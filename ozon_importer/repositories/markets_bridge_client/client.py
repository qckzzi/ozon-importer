import uuid
from http import HTTPStatus
from typing import Any

from async_property import async_property
from backoff import expo, on_exception
from httpx import AsyncClient, HTTPError, HTTPStatusError, Response

from ozon_importer.interfaces import ILogger
from ozon_importer.repositories.markets_bridge_client.types import (
    Brand,
    Category,
    Characteristic,
    CharacteristicValue,
    Image,
    Product,
)


class MarketsBridgeClient:
    def __init__(
        self,
        http_client: AsyncClient,
        markets_bridge_host: str,
        markets_bridge_login: str,
        markets_bridge_password: str,
    ) -> None:
        self.http_client: AsyncClient = http_client
        self.markets_bridge_host: str = markets_bridge_host
        self.accessor: Accessor = Accessor(
            http_client=http_client,
            markets_bridge_host=markets_bridge_host,
            login=markets_bridge_login,
            password=markets_bridge_password,
        )

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]"

    async def send_product(self, product: Product, logger: ILogger | None = None) -> tuple[int, bool]:
        """Send product.

        Returns:
            product_id, is_new.
        """
        product_id, is_new = await self._send_entity(
            product,
            f"{self.markets_bridge_host}api/v1/provider/products/",
            logger=logger,
        )
        logger.debug(f"{self} sends '{product['name']}' product, {product_id=}, {is_new=}")

        return product_id, is_new

    async def send_category(
        self,
        category: Category,
        logger: ILogger | None = None,
    ) -> tuple[int, bool]:
        """Send category.

        Returns:
            category_id, is_new.
        """
        category_id, is_new = await self._send_entity(
            category,
            f"{self.markets_bridge_host}api/v1/provider/categories/",
            logger=logger,
        )
        logger.debug(f"{self} sends '{category['name']}' characteristic, {category_id=}, {is_new=}")

        return category_id, is_new

    async def send_characteristic(
        self,
        characteristic: Characteristic,
        logger: ILogger | None = None,
    ) -> tuple[int, bool]:
        """Send characteristic.

        Returns:
            characteristic_id, is_new.
        """
        characteristic_id, is_new = await self._send_entity(
            characteristic,
            f"{self.markets_bridge_host}api/v1/provider/characteristics/",
            logger=logger,
        )
        logger.debug(f"{self} sends '{characteristic['name']}' characteristic, {characteristic_id=}, {is_new=}")

        return characteristic_id, is_new

    async def send_characteristic_value(
        self,
        characteristic_value: CharacteristicValue,
        logger: ILogger | None = None,
    ) -> tuple[int, bool]:
        """Send characteristic value.

        Returns:
            characteristic_value_id, is_new.
        """
        characteristic_value_id, is_new = await self._send_entity(
            characteristic_value,
            f"{self.markets_bridge_host}api/v1/provider/characteristic_values/",
            logger=logger,
        )
        logger.debug(
            f"{self} sends '{characteristic_value['value']}' "
            f"characteristic value, {characteristic_value_id=}, {is_new=}",
        )

        return characteristic_value_id, is_new

    async def send_brand(self, brand: Brand, logger: ILogger | None = None) -> tuple[int, bool]:
        """Send brand.

        Returns:
            brand_id, is_new.
        """
        brand_id, is_new = await self._send_entity(
            brand,
            f"{self.markets_bridge_host}api/v1/provider/brands/",
            logger=logger,
        )
        if logger:
            logger.debug(f"{self} sends '{brand['name']}' brand, {brand_id=}, {is_new=}")

        return brand_id, is_new

    @on_exception(expo, HTTPError, max_tries=3)
    async def send_image(self, image: Image, logger: ILogger | None = None) -> int:
        """Send image.

        Returns:
            image_id.
        """
        if logger:
            logger.debug(f"{self}: sends image for {image['product_id']}")

        headers: dict = await self._get_authorization_headers()
        response: Response = await self.http_client.post(
            f"{self.markets_bridge_host}api/v1/provider/product_images/",
            data={"product": image["product_id"]},
            files={"image": (f"{uuid.uuid4().hex}.jpg", image["body"])},
            headers=headers,
        )

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            await self.accessor.update_access_token()

            return self.send_image(image, logger)

        try:
            response.raise_for_status()
        except HTTPStatusError:
            if HTTPStatus(response.status_code).is_server_error and logger:
                logger.debug("Internal server error")
            raise

        return response.json()["id"]

    @on_exception(expo, HTTPError, max_tries=3)
    async def _send_entity(self, entity: dict, url: str, logger: ILogger | None = None) -> tuple[int, bool]:
        """Send entity.

        Returns:
            entity_id, is_new.
        """
        headers: dict = await self._get_authorization_headers()
        response: Response = await self.http_client.post(url, json=entity, headers=headers)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            await self.accessor.update_access_token()

            return await self._send_entity(entity, url, logger)

        try:
            response.raise_for_status()
        except HTTPStatusError:
            if HTTPStatus(response.status_code).is_server_error and logger:
                logger.debug("Internal server error")
            raise

        return response.json()["id"], response.status_code == HTTPStatus.CREATED

    async def _get_authorization_headers(self) -> dict:
        access_token: str = await self.accessor.access_token

        return {"Authorization": f"Bearer {access_token}"}


class Accessor:
    def __init__(
        self,
        *,
        http_client: AsyncClient,
        markets_bridge_host: str,
        login: str,
        password: str,
    ) -> None:
        self.http_client: AsyncClient = http_client
        self.markets_bridge_host: str = markets_bridge_host
        self.login: str = login
        self.password: str = password
        self._refresh_token: str | None = None
        self._access_token: str | None = None

    @async_property
    async def access_token(self) -> str:
        if not self._access_token:
            await self.update_jwt()

        return self._access_token

    async def update_jwt(self) -> None:
        login_data: dict = {
            "username": self.login,
            "password": self.password,
        }

        response: Response = await self.http_client.post(f"{self.markets_bridge_host}api/token/", json=login_data)
        response.raise_for_status()
        token_data: Any = response.json()
        self._access_token = token_data["access"]
        self._refresh_token = token_data["refresh"]

    async def update_access_token(self) -> None:
        body: dict = {"refresh": self._refresh_token}

        response: Response = await self.http_client.post(f"{self.markets_bridge_host}api/token/refresh/", json=body)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            await self.update_jwt()
            await self.update_access_token()

            return

        response.raise_for_status()

        token_data: Any = response.json()
        self._access_token = token_data["access"]
