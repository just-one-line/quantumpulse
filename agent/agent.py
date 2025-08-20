import datetime
from agent.storage import Storage

class TradingAgent:
    def __init__(self):
        self.storage = Storage()

    def generate_signal(self, market_data):
        """
        Example rule-based strategy:
        - If price goes up more than 1% in 5 minutes → BUY
        - If price goes down more than 1% in 5 minutes → SELL
        - Otherwise → HOLD
        """

        signal = "HOLD"
        change = (market_data["close"] - market_data["open"]) / market_data["open"]

        if change > 0.01:
            signal = "BUY"
        elif change < -0.01:
            signal = "SELL"

        # Save signal to storage
        self.storage.save_signal({
            "time": datetime.datetime.utcnow().isoformat(),
            "signal": signal,
            "price": market_data["close"]
        })

        return signal

    def get_latest_signals(self, limit=10):
        """Fetch recent trading signals from storage"""
        return self.storage.load_signals(limit=limit)
