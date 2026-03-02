import yfinance as yf
from flask_socketio import SocketIO, emit, join_room
from threading import Thread
import time


def stock_webSocket(data, socketio: SocketIO):
    symbol = data.get("symbol")

    if symbol:
        join_room(symbol)

        def message_handler(msg):
            # print(f"Yahoo msg: {msg}")  # Debug
            price = msg.get("price")
            if price:
                socketio.emit(
                    "price_update",
                    {"symbol": symbol, "price": float(price)},
                    room=symbol,
                )

        def start_stream():
            try:
                ws = yf.WebSocket(verbose=True)
                ws.subscribe(symbol)
                ws.listen(message_handler)  # Now runs forever
            except Exception as e:
                print(f"WS error: {e}", symbol)

        # ✅ THREAD IT - non-blocking!
        Thread(target=start_stream, daemon=True).start()
        emit("status", {"msg": f"Subscribed to {symbol}"})
