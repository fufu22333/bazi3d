class ProviderRegistry:
    def __init__(self, providers: dict | None = None) -> None:
        self._providers = providers or {}

    def register(self, provider_key: str, provider) -> None:
        self._providers[provider_key] = provider

    def get(self, provider_key: str):
        if provider_key not in self._providers:
            raise KeyError(f"Unknown provider: {provider_key}")
        return self._providers[provider_key]
