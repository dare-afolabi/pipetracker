import os
import re
from typing import Optional
import logging
from cryptography.fernet import Fernet
from pathlib import Path
from filelock import FileLock

logger = logging.getLogger(__name__)


def get_or_create_key(
    env_var: str = "APP_SECRET_KEY", key_file: str = ".secret.key"
) -> bytes:
    """Generate or retrieve an encryption key from an \
        environment variable or file."""
    key: Optional[bytes] = None  # Changed from `bytes | None`
    env_key = os.getenv(env_var)
    lock = FileLock(f"{key_file}.lock")
    with lock:
        if env_key:
            key = env_key.encode()
        elif Path(key_file).exists():
            key = Path(key_file).read_bytes()
        else:
            key = Fernet.generate_key()
            Path(key_file).write_bytes(key)
            logger.warning(
                f"No {env_var} found — new key generated\
                     and stored in {key_file}"
            )
    return key


def get_secret(
    name: str,
    env_var: Optional[str] = None,
    file_path: Optional[str] = None,
    encrypt_key: Optional[bytes] = None,
) -> str:
    """
    Get a secret from environment variable, then optionally an encrypted file.
    Raises ValueError if secret is not found.
    """
    env_var = env_var or name
    secret = os.getenv(env_var)
    if secret:
        return secret
    if file_path:
        path = Path(file_path)
        if path.exists():
            data = path.read_bytes()
            if encrypt_key:
                cipher = Fernet(encrypt_key)
                return cipher.decrypt(data).decode()
            return data.decode()
    raise ValueError(
        f"Secret '{name}' not found in env var '{env_var}' or file {file_path}"
    )


class Security:
    """
    Handles log encryption, decryption, PII masking, and plugin secrets.
    """

    def __init__(
        self,
        encrypt_logs: bool = False,
        key_env: str = "APP_SECRET_KEY",
        key_file: str = ".secret.key",
    ):
        self.encrypt_logs = encrypt_logs
        self.key: Optional[bytes] = (  # Changed from `bytes | None`
            get_or_create_key(env_var=key_env, key_file=key_file)
            if encrypt_logs
            else None
        )
        self.cipher = Fernet(self.key) if self.key else None

    def mask_pii(self, log_line: str) -> str:
        """Mask emails and long numbers in logs."""
        log_line = re.sub(
            r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", "[REDACTED_EMAIL]", log_line
        )
        log_line = re.sub(r"\b\d{4,}\b", "[REDACTED_NUMBER]", log_line)
        return log_line

    def encrypt_log(self, log_line: str) -> str:
        if self.encrypt_logs and self.cipher:
            return self.cipher.encrypt(log_line.encode()).decode()
        return log_line

    def decrypt_log(self, log_line: str) -> str:
        if self.encrypt_logs and self.cipher:
            try:
                return self.cipher.decrypt(log_line.encode()).decode()
            except Exception as e:
                logger.warning(f"Failed to decrypt line: {e}")
                return log_line
        return log_line

    def get_plugin_secret(
        self,
        name: str,
        file_path: Optional[str] = None,
        env_var: Optional[str] = None,
    ) -> str:
        """
        Retrieve a plugin/API secret safely.
        Looks for the secret in env var first,\
             then optionally an encrypted file.
        Supports plugin-specific naming conventions\
             (e.g., DD_API_KEY for Datadog).
        """
        env_var = env_var or f"{name.upper()}_SECRET"
        file_path = file_path or f".{name.lower()}_secret"
        return get_secret(
            name=name,
            env_var=env_var,
            file_path=file_path,
            encrypt_key=self.key if self.encrypt_logs else None,
        )
