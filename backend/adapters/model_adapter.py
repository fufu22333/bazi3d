from abc import ABC, abstractmethod
from typing import TypedDict


class NormalizedModelResult(TypedDict):
    url: str
    format: str
    metadata: dict


class ModelAdapter(ABC):
    @abstractmethod
    def submit(self, prompt: dict, config: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def query(self, task_id: str) -> dict:
        raise NotImplementedError

    def normalize(self, result: dict) -> NormalizedModelResult:
        required_keys = {"url", "format", "metadata"}
        if set(result.keys()) != required_keys:
            raise ValueError("normalize result must contain url, format and metadata")

        if not isinstance(result["url"], str) or not result["url"]:
            raise ValueError("normalize result url must be a non-empty string")
        if not isinstance(result["format"], str) or not result["format"]:
            raise ValueError("normalize result format must be a non-empty string")
        if not isinstance(result["metadata"], dict):
            raise ValueError("normalize result metadata must be a dict")

        return {
            "url": result["url"],
            "format": result["format"],
            "metadata": result["metadata"],
        }
