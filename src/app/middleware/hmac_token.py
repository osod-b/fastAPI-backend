import hmac
import hashlib
from datetime import datetime
from typing import Optional

from core.config import setting



class TokenController:
    def __init__(self):

        assert type(setting.SSH_KEY) == str
        assert type(setting.HMAC_MESSAGE) == str

        self.secret = bytearray(setting.SSH_KEY, "utf-8")
        self.message = bytearray(setting.HMAC_MESSAGE, "utf-8")
        
        self.signature = self.create_signature()
        self.last_time: Optional[str] = None

    def create_signature(self) -> str:
        return hmac.new(self.secret, self.message, hashlib.sha256).hexdigest()
    
    def compare_signatures(self, foreign_signature: str) -> bool:
        self.last_time = datetime.now().strftime("%H-%M-%S")
        return hmac.compare_digest(self.signature, foreign_signature)