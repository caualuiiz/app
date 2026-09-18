import asyncio
import os

from ai.claude_provider import ClaudeProvider
from db import get_db


async def main() -> None:
    required = ("MONGO_URL", "DB_NAME", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        raise SystemExit("Configuração ausente: " + ", ".join(missing))

    db = get_db()
    await db.command("ping")
    print("MongoDB: OK")

    provider = ClaudeProvider()
    result = await provider.generate_structured_decision(
        system_prompt=(
            "Você é um diretor de arte digital. Retorne uma decisão visual mínima e objetiva. "
            "Use somente os dados fornecidos."
        ),
        context={
            "company": {
                "name": "Teste de integração",
                "business_type": "barbearia",
                "description": "Barbearia masculina de bairro",
                "city": "São Gonçalo",
            },
            "landing": {
                "hero": "Cortes modernos com atendimento personalizado",
                "style": "premium e contemporâneo",
            },
            "visual_intelligence": None,
            "reference_intelligence": None,
            "art_direction": None,
            "design_system": None,
            "layout_plan": None,
        },
        schema_description="Retorne summary, actions, confidence, warnings e missing_data.",
    )
    print("Claude: OK")
    print("Modelo:", provider.model)
    print("Resumo:", result["summary"])
    print("Confiança:", result["confidence"])


if __name__ == "__main__":
    asyncio.run(main())