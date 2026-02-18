"""Collector base types."""

from __future__ import annotations

import abc


class AsyncCollector(abc.ABC):
    @abc.abstractmethod
    async def run(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
