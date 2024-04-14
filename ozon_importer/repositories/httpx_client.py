from collections.abc import Callable
from functools import partial
from typing import Any, Literal, get_args

from backoff import expo, on_exception
from httpx import AsyncClient, ConnectError, ConnectTimeout, Response


ProxyMethod = Literal["get", "options", "head", "post", "put", "patch", "delete"]


class HttpxClient:
    def __init__(self, session: AsyncClient) -> None:
        self.session: AsyncClient = session

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}]"

    def __getattr__(self, attribute: ProxyMethod) -> partial:  # type: ignore[misc]
        if attribute not in get_args(ProxyMethod):
            raise AttributeError(f"{self} has no attribute '{attribute}'")

        method: Callable = getattr(self.session, attribute)

        return partial(self._request, method=method)

    @on_exception(expo, (ConnectError, ConnectTimeout), max_tries=3)
    async def _request(self, url: str, *, method: Callable, **kwargs: Any) -> Response:
        resp: Response = await method(url, **kwargs)
        resp.read()

        return resp
