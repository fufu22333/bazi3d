import httpx

from backend.adapters.model_adapter import ModelAdapter


class ModelProviderError(Exception):
    pass


class HunyuanAdapter(ModelAdapter):
    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        endpoint: str = "https://ai3d.tencentcloudapi.com/",
        version: str = "2025-05-13",
        region: str = "ap-guangzhou",
        timeout: float = 30.0,
        request_callable=None,
    ) -> None:
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.version = version
        self.region = region
        self.timeout = timeout
        self.request_callable = request_callable or self._request

    def _request(self, method: str, url: str, **kwargs) -> dict:
        response = httpx.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def _headers(self, action: str) -> dict:
        return {
            "Content-Type": "application/json",
            "X-TC-Action": action,
            "X-TC-Version": self.version,
            "X-TC-Region": self.region,
            "X-TC-SecretId": self.secret_id,
            "X-TC-SecretKey": self.secret_key,
        }

    def submit(self, prompt: dict, config: dict) -> str:
        payload = {**config, **prompt}
        try:
            response = self.request_callable(
                "POST",
                self.endpoint,
                headers=self._headers("SubmitHunyuanTo3DProJob"),
                json=payload,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise ModelProviderError("Hunyuan submit failed") from exc

        return response["Response"]["JobId"]

    def query(self, task_id: str) -> dict:
        try:
            return self.request_callable(
                "POST",
                self.endpoint,
                headers=self._headers("QueryHunyuanTo3DProJob"),
                json={"JobId": task_id},
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise ModelProviderError("Hunyuan query failed") from exc

    def normalize(self, result: dict) -> dict:
        response = result["Response"]
        first_file = response["ResultFile3Ds"][0]
        return super().normalize(
            {
                "url": first_file["Url"],
                "format": first_file["Type"].lower(),
                "metadata": {
                    "provider": "hunyuan",
                    "task_id": response.get("JobId"),
                    "status": response.get("Status"),
                    "thumbnail_url": first_file.get("PreviewImageUrl"),
                },
            }
        )
