from collections.abc import Sequence

from bakery import Bakery, Cake
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitRoute, RabbitRouter
from httpx import AsyncClient

from ozon_importer.config import Settings
from ozon_importer.handlers.parsed_loading import ParsedLoadingHandler
from ozon_importer.repositories.http_fetcher import HttpFetcher
from ozon_importer.repositories.httpx_client import HttpxClient
from ozon_importer.repositories.markets_bridge_client.client import MarketsBridgeClient
from ozon_importer.services.product_importer import ProductImporter


class Container(Bakery):
    settings: Settings = Cake(Settings)  # type: ignore[assignment]

    broker: RabbitBroker = Cake(RabbitBroker, settings.amqp_dsn_str)
    _httpx_client: HttpxClient = Cake(
        HttpxClient,
        session=Cake(
            AsyncClient,
            timeout=settings.http_timeout,
        ),
    )
    _markets_bridge_client: MarketsBridgeClient = Cake(
        MarketsBridgeClient,
        http_client=_httpx_client,
        markets_bridge_host=settings.markets_bridge_host,
        markets_bridge_login=settings.markets_bridge_login,
        markets_bridge_password=settings.markets_bridge_password,
    )
    _http_fetcher: HttpFetcher = Cake(HttpFetcher, _httpx_client)
    _product_importer: ProductImporter = Cake(ProductImporter, _markets_bridge_client, _http_fetcher, settings.ozon_id)
    _parsed_loading_handler: ParsedLoadingHandler = Cake(ParsedLoadingHandler, _product_importer)
    _parsed_loading_queue: RabbitQueue = Cake(RabbitQueue, settings.parsed_loading_queue, durable=True)
    _parsed_loading_route: RabbitRoute = Cake(RabbitRoute, _parsed_loading_handler, _parsed_loading_queue)

    _routes: Sequence[RabbitRoute] = (_parsed_loading_route,)
    router: RabbitRouter = Cake(RabbitRouter, handlers=_routes)
