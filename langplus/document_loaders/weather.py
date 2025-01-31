"""Simple reader that reads weather data from OpenWeatherMap API"""
from __future__ import annotations

from datetime import datetime
from typing import Iterator, List, Optional, Sequence

from langplus.docstore.document import Document
from langplus.document_loaders.base import BaseLoader
from langplus.utilities.openweathermap import OpenWeatherMapAPIWrapper


class WeatherDataLoader(BaseLoader):
    """Weather Reader.

    Reads the forecast & current weather of any location using OpenWeatherMap's free
    API. Checkout 'https://openweathermap.org/appid' for more on how to generate a free
    OpenWeatherMap API.
    """

    def __init__(
        self,
        client: OpenWeatherMapAPIWrapper,
        places: Sequence[str],
    ) -> None:
        """Initialize with parameters."""
        super().__init__()
        self.client = client
        self.places = places

    @classmethod
    def from_params(
        cls, places: Sequence[str], *, openweathermap_api_key: Optional[str] = None
    ) -> WeatherDataLoader:
        client = OpenWeatherMapAPIWrapper(openweathermap_api_key=openweathermap_api_key)
        return cls(client, places)

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazily load weather data for the given locations."""
        for place in self.places:
            metadata = {"queried_at": datetime.now()}
            content = self.client.run(place)
            yield Document(page_content=content, metadata=metadata)

    def load(
        self,
    ) -> List[Document]:
        """Load weather data for the given locations."""
        return list(self.lazy_load())
