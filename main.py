from fastapi import FastAPI
from tradingview_ta import TA_Handler, Interval
import requests
from twilio.rest import Client
import os

app = FastAPI()

@app.get("/sinal")
def gerar_sinal():
    handler = TA_Handler(
        symbol="EURUSD",
        exchange="FX_IDC",
        screener="forex",
        interval=Interval.INTERVAL_5_MINUTES,
    )

    analysis = handler.get_analysis()
    recomendacao = analysis.summary["RECOMMENDATION"]
    rsi = analysis.indicators["RSI"]
    tipo = "CALL" if recomendacao == "STRONG_BUY" else "PUT" if recomendacao == "STRONG_SELL" else "AGUARDAR"

    mensagem = f"SINAL EUR/USD\n🔹 Tipo: {tipo}\n🔸 Força: {recomendacao}\n📈 RSI: {round(rsi, 2)}"
    
    if tipo != "AGUARDAR":
        enviar_telegram(mensagem)
        enviar_whatsapp(mensagem)

    return {
        "ativo": "EUR/USD",
        "recomendacao": recomendacao,
        "tipo": tipo,
        "rsi": round(rsi, 2)
    }

def enviar_telegram(mensagem):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    dados = {"chat_id": chat_id, "text": mensagem}
    requests.post(url, data=dados)

def enviar_whatsapp(mensagem):
    account_sid = os.getenv('TWILIO_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=mensagem,
        to='whatsapp:+SEU_NUMERO'
    )
