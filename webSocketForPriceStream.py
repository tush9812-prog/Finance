import yfinance as yf
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime, timezone
import time


def stock_webSocket(data, socketio):
    symbol = data.get("symbol")  # ✅ ['AAPL']
    print(f"Streaming: {symbol}")
    if symbol:
        join_room(symbol)

        def message_handler(msg):
            symbol = msg.get("id")
            socketio.emit(
                "price_update",
                {
                    "symbol": msg.get("id"),
                    "price": msg.get("price"),
                    "time": int(datetime.now(timezone.utc).timestamp()),
                },
                room=symbol,
            )

        # socketio.emit("price_update", msg)  # ✅ Broadcast

        # ✅ FIXED: WS outside handler, in thread
        def start_stream():

            ws = yf.WebSocket()
            ws.subscribe(symbol)
            ws.listen(message_handler)  # Now runs continuously
