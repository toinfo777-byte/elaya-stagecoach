from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class SceneBase:
    """Базовая структура сцены Элайи."""
    name: str
    emoji: str
    action: Callable[..., Awaitable[str]]

    async def run(self, *args, **kwargs) -> str:
        return await self.action(*args, **kwargs)
