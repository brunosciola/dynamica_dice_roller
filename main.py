import json
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
from comandos import ComandoBot

load_dotenv()

with open("config.json", "r") as f:
    config = json.load(f)

plataforma = config["plataforma"]

if plataforma != "stoat":
    print(f"Plataforma configurada: {plataforma}")
    print("Este main.py é para Stoat. Ajuste config.json.")
    exit()

token_env = config["stoat"]["token_env"]
TOKEN = os.getenv(token_env)

if not TOKEN:
    print(f"Token não encontrado. Verifique se {token_env} está definido no .env")
    exit()

comando_bot = ComandoBot()

API_URL = "https://api.revolt.chat"
WS_URL = "wss://ws.revolt.chat"

async def send_message(session, token, channel_id, content):
    headers = {
        "x-bot-token": token,
        "Content-Type": "application/json"
    }
    async with session.post(
        f"{API_URL}/channels/{channel_id}/messages",
        headers=headers,
        json={"content": content}
    ) as resp:
        if resp.status != 200:
            print(f"Erro ao enviar mensagem: {resp.status}")

async def main():
    async with aiohttp.ClientSession() as session:
        # Autentica e obtém informações do bot
        headers = {"x-bot-token": TOKEN}
        async with session.get(f"{API_URL}/users/@me", headers=headers) as resp:
            if resp.status != 200:
                print(f"Erro de autenticação: {resp.status}")
                return
            bot_info = await resp.json()
            bot_id = bot_info["_id"]
            print(f"Bot {bot_info.get('username', 'Desconhecido')} conectado ao Stoat!")

        # Conecta ao WebSocket
        ws = await session.ws_connect(WS_URL)
        await ws.send_json({"type": "Authenticate", "token": TOKEN})

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                
                if data.get("type") == "Message":
                    author_id = data.get("author")
                    
                    # Ignora mensagens do próprio bot
                    if author_id == bot_id:
                        continue

                    channel_id = data.get("channel")
                    content = data.get("content", "")
                    
                    # Tenta obter nome do autor
                    nome_exibicao = "Usuário"
                    try:
                        async with session.get(f"{API_URL}/users/{author_id}", headers=headers) as resp:
                            if resp.status == 200:
                                user_info = await resp.json()
                                nome_exibicao = user_info.get("display_name") or user_info.get("username", "Usuário")
                    except:
                        pass

                    resposta = comando_bot.processar(channel_id, author_id, nome_exibicao, content)

                    if resposta:
                        await send_message(session, TOKEN, channel_id, resposta)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {msg}")
                break

if __name__ == "__main__":
    asyncio.run(main())