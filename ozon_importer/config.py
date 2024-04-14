from pydantic import AmqpDsn, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    amqp_dsn: AmqpDsn
    parsed_loading_queue_prefix: str = "parsed_loading."

    ozon_id: int
    ozon_name: str = "ozon"

    markets_bridge_host: HttpUrl
    markets_bridge_login: str
    markets_bridge_password: str

    http_timeout: float = 100000.0

    @property
    def parsed_loading_queue(self) -> str:
        return f"{self.parsed_loading_queue_prefix}{self.ozon_name}"

    @property
    def mb_products_url(self) -> str:
        return f"{self.markets_bridge_host}api/v1/provider/products/"

    @property
    def mb_characteristics_url(self) -> str:
        return f"{self.markets_bridge_host}api/v1/provider/characteristics/"

    @property
    def mb_characteristic_values_url(self) -> str:
        return f"{self.markets_bridge_host}api/v1/provider/characteristic_values/"

    @property
    def mb_product_images_url(self) -> str:
        return f"{self.markets_bridge_host}api/v1/provider/product_images/"

    @property
    def mb_brands_url(self) -> str:
        return f"{self.markets_bridge_host}api/v1/provider/brands/"

    @property
    def mb_token_url(self) -> str:
        return f"{self.markets_bridge_host}api/token/"

    @property
    def mb_token_refresh_url(self) -> str:
        return f"{self.mb_token_url}refresh/"

    @property
    def amqp_dsn_str(self) -> str:
        return self.amqp_dsn.unicode_string()
