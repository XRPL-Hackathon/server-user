from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class User:
    def __init__(self, wallet: str, point: int):
        self.wallet = wallet
        self.point = point

    def __repr__(self):
        return f"User(wallet={self.wallet}, point={self.point})"