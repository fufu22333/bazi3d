import httpx

from backend.adapters.model_adapter import ModelAdapter


class ModelProviderError(Exception):
    pass


class MeshyAdapter(ModelAdapter):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.meshy.ai",
        timeout: float = 30.0,
        request_callable=None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.request_callable = request_callable or self._request

    def _request(self, method: str, url: str, **kwargs) -> dict:
        response = httpx.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def submit(self, prompt: dict, config: dict) -> str:
        payload = {**config, **prompt}
        url = f"{self.base_url}/openapi/v2/text-to-3d"
        try:
            response = self.request_callable(
                "POST",
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise ModelProviderError("Meshy submit failed") from exc

        return response["result"]

    def query(self, task_id: str) -> dict:
        url = f"{self.base_url}/openapi/v2/text-to-3d/{task_id}"
        try:
            return self.request_callable(
                "GET",
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise ModelProviderError("Meshy query failed") from exc

    def normalize(self, result: dict) -> dict:
        normalized = super().normalize(
            {
                "url": result["model_urls"]["glb"],
                "format": "glb",
                "metadata": {
                    "provider": "meshy",
                    "task_id": result.get("id"),
                    "status": result.get("status"),
                    "thumbnail_url": result.get("thumbnail_url"),
                },
            }
        )
        return normalized
