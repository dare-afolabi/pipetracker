import os
import re
from cryptography.fernet import Fernet


class Security:
    """Handles log encryption, decryption, and PII masking."""

    def __init__(self, encrypt_logs: bool = False):
        self.encrypt_logs = encrypt_logs
        key = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
        self.cipher = Fernet(key) if encrypt_logs else None

    def mask_pii(self, log_line: str) -> str:
        """Redact sensitive information such as emails and long numeric IDs."""
        log_line = re.sub(
            r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", "[REDACTED_EMAIL]", log_line
        )
        log_line = re.sub(r"\b\d{4,}\b", "[REDACTED_NUMBER]", log_line)
        return log_line

    def encrypt_log(self, log_line: str) -> str:
        """Encrypt a log line if encryption is enabled."""
        if self.encrypt_logs and self.cipher:
            return self.cipher.encrypt(log_line.encode()).decode()
        return log_line

    def decrypt_log(self, log_line: str) -> str:
        """Decrypt a log line if encryption is enabled."""
        if self.encrypt_logs and self.cipher:
            try:
                return self.cipher.decrypt(log_line.encode()).decode()
            except Exception:
                # Return unmodified if the line was not actually encrypted
                return log_line
        return log_line
