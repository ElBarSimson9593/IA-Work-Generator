class Ollama:
    def __init__(self, model: str = "mixtral") -> None:
        self.model = model

    def __call__(self, prompt: str) -> str:
        return "stub"

class OllamaEndpointNotFoundError(Exception):
    pass
