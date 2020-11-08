import pytest
import asyncio
from aioletterxpress.client import LetterxpressClient


@pytest.fixture
def client() -> LetterxpressClient:
    c = LetterxpressClient()
    return c


@pytest.fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
