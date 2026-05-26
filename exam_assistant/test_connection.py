import sys
from openai import OpenAI

from config import AppConfig

def main():
    cfg = AppConfig.from_file()

    print(f"--- DIAGNÓSTICO DE CONEXIÓN ---")
    print(f"Modelo: {cfg.model}")
    print(f"Base URL: {cfg.base_url}")
    
    if not cfg.api_key:
        print("Error: No se detectó OPENROUTER_API_KEY en config.env")
        return 1

    client = OpenAI(base_url=cfg.base_url, api_key=cfg.api_key)

    try:
        response = client.chat.completions.create(
            model=cfg.model,
            messages=[{"role": "user", "content": "Hola, responde solo con la palabra OK."}],
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 1024
            }
        )
        print(f"Respuesta recibida: {response.choices[0].message.content}")
        print("--- PRUEBA EXITOSA ---")
        return 0
    except Exception as e:
        print(f"--- ERROR EN LA PRUEBA ---")
        print(e)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
