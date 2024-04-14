import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from ozon_importer.container import Container


async def bake_container() -> None:
    await Container.aopen()


asyncio.run(bake_container())

broker: RabbitBroker = Container.broker()  # type: ignore[operator]
broker.include_router(Container.router())  # type: ignore[operator]
app = FastStream(broker)


@app.after_shutdown
async def on_shutdown() -> None:
    await Container.aclose()
