from backoff import expo, on_exception
from httpx import AsyncClient, HTTPError, Response

from ozon_importer.interfaces import ILogger


class HttpFetcher:
    def __init__(self, http_client: AsyncClient) -> None:
        self.http_client: AsyncClient = http_client

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]"

    @on_exception(expo, HTTPError, max_tries=3)
    async def fetch(self, url: str, logger: ILogger | None = None) -> bytes:
        if logger:
            logger.debug(f"{self}: fetches {url=}")

        response: Response = await self.http_client.get(url)

        return response.content
