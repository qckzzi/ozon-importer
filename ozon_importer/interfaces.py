from typing import Any, Protocol


class ILogger(Protocol):
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
