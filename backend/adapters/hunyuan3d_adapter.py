from __future__ import annotations

import time
from typing import Any

from backend.adapters.model_adapter import ModelAdapter


class Hunyuan3DAdapterError(Exception):
    pass


class Hunyuan3DAdapter(ModelAdapter):
    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        region: str = "ap-guangzhou",
        endpoint: str = "ai3d.tencentcloudapi.com",
        version: str = "2025-05-13",
        poll_interval: float = 5.0,
        max_poll_attempts: int = 120,
        client=None,
    ) -> None:
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.endpoint = endpoint or "ai3d.tencentcloudapi.com"
        self.version = version
        self.poll_interval = poll_interval
        self.max_poll_attempts = max_poll_attempts
        self._client = client

    @staticmethod
    def _truncate_prompt(prompt: str, limit: int = 1024) -> str:
        trimmed = prompt.strip()
        if len(trimmed) <= limit:
            return trimmed

        candidate = trimmed[:limit]
        sentence_end = candidate.rfind(".")
        if sentence_end != -1:
            return candidate[: sentence_end + 1].strip()
        return candidate.strip()

    def _build_client(self):
        if self._client is not None:
            return self._client
        if not self.secret_id or not self.secret_key:
            raise Hunyuan3DAdapterError(
                "Tencent Cloud credentials are missing. Set TENCENTCLOUD_SECRET_ID and TENCENTCLOUD_SECRET_KEY."
            )

        try:
            from tencentcloud.common import credential
            from tencentcloud.common.common_client import CommonClient
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
        except ImportError as exc:
            raise Hunyuan3DAdapterError(
                "tencentcloud-sdk-python is not installed."
            ) from exc

        credentials = credential.Credential(self.secret_id, self.secret_key)
        http_profile = HttpProfile(endpoint=self.endpoint)
        client_profile = ClientProfile(httpProfile=http_profile)
        module = self.endpoint.split(".", 1)[0]
        self._client = CommonClient(module, self.version, credentials, self.region, profile=client_profile)
        return self._client

    def submit_job(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise Hunyuan3DAdapterError("Prompt must be a non-empty string.")

        prompt = self._truncate_prompt(prompt)
        try:
            response = self._build_client().call_json(
                "SubmitHunyuanTo3DProJob",
                {"Prompt": prompt.strip()},
            )
        except Exception as exc:
            raise Hunyuan3DAdapterError("Failed to submit Hunyuan 3D job.") from exc

        job_id = (response or {}).get("Response", {}).get("JobId")
        if not job_id:
            raise Hunyuan3DAdapterError("Hunyuan 3D submit response missing JobId.")
        return job_id

    def query_job(self, job_id: str) -> dict[str, Any]:
        if not isinstance(job_id, str) or not job_id.strip():
            raise Hunyuan3DAdapterError("Job ID must be a non-empty string.")

        last_response: dict[str, Any] | None = None
        for _ in range(self.max_poll_attempts):
            try:
                response = self._build_client().call_json(
                    "QueryHunyuanTo3DProJob",
                    {"JobId": job_id},
                )
            except Exception as exc:
                raise Hunyuan3DAdapterError("Failed to query Hunyuan 3D job.") from exc

            last_response = response
            status = (response or {}).get("Response", {}).get("Status")
            if status == "DONE":
                return response
            if status == "FAIL":
                payload = response.get("Response", {})
                message = payload.get("ErrorMessage") or "Hunyuan 3D job failed."
                code = payload.get("ErrorCode") or "unknown_error"
                raise Hunyuan3DAdapterError(f"{code}: {message}")
            time.sleep(self.poll_interval)

        raise Hunyuan3DAdapterError(
            f"Hunyuan 3D job polling timed out for {job_id}. Last response: {last_response}"
        )

    def submit(self, prompt: dict, config: dict) -> str:
        prompt_text = prompt.get("Prompt") or config.get("Prompt") or ""
        return self.submit_job(prompt_text)

    def query(self, task_id: str) -> dict[str, Any]:
        return self.query_job(task_id)

    def normalize(self, result: dict) -> dict:
        response = result.get("Response", {})
        files = response.get("ResultFile3Ds") or []
        glb_file = next(
            (
                item
                for item in files
                if str(item.get("Type", "")).upper() == "GLB" and item.get("Url")
            ),
            None,
        )
        if glb_file is None:
            raise Hunyuan3DAdapterError("Hunyuan 3D response missing GLB result.")

        return super().normalize(
            {
                "url": glb_file["Url"],
                "format": "glb",
                "metadata": {
                    "provider": "hunyuan3d",
                    "task_id": response.get("JobId"),
                    "status": response.get("Status"),
                    "thumbnail_url": glb_file.get("PreviewImageUrl"),
                    "result_files": files,
                },
            }
        )
