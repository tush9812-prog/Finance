import yfinance as yf
from flask_socketio import SocketIO, emit
import threading


def stock_webSocket(data, socketio):
    symbols = data["symbols"]  # ✅ ['AAPL']
    print(f"Streaming: {symbols}")

    def message_handler(msg):
        socketio.emit("price_update", msg)  # ✅ Broadcast

    # ✅ FIXED: WS outside handler, in thread
    def start_stream():
        ws = yf.WebSocket()
        ws.subscribe(symbols)
        ws.listen(message_handler)  # Now runs continuously

    thread = threading.Thread(target=start_stream, daemon=True)
    thread.start()
