"""
This program is free software: you can redistribute it under the terms
of the GNU General Public License, v. 3.0. If a copy of the GNU General
Public License was not distributed with this file, see <https://www.gnu.org/licenses/>.
"""

import os
import base64
import argparse
import uuid
import json
import random
from typing import Optional

from smswithoutborders_libsig.keypairs import x25519
from base_logger import get_logger
from src.utils import get_configs, load_key
from src.db_models import StaticKeypairs
from src.crypto import encrypt_aes, decrypt_aes

logger = get_logger("static.x25519.keygen")

ENCRYPTION_KEY = load_key(get_configs("SHARED_KEY"), 32)
STATIC_KEYSTORE_PATH = get_configs("STATIC_X25519_KEYSTORE_PATH", strict=True)


def generate_keypair(kid: int) -> None:
    """Generates a keypair, encrypts it, and stores it in the database."""
    keystore_path: Optional[str] = None
    try:
        keystore_path = os.path.join(STATIC_KEYSTORE_PATH, f"{uuid.uuid4()}.db")
        keypair_obj = x25519(keystore_path)
        keypair_obj.init()

        keypair_ciphertext = encrypt_aes(
            ENCRYPTION_KEY, keypair_obj.serialize(), is_bytes=True
        )

        StaticKeypairs.create_keypair(
            kid=kid, keypair_bytes=keypair_ciphertext, status="active"
        )
        logger.info("Successfully generated and stored keypair %d.", kid)

    except Exception as e:
        logger.exception("Failed to generate keypair %d: %s", kid, e)

        if keystore_path and os.path.exists(keystore_path):
            try:
                os.remove(keystore_path)
                logger.info("Rolled back and deleted keystore file: %s", keystore_path)
            except Exception as rollback_error:
                logger.error(
                    "Failed to delete keystore file %s: %s",
                    keystore_path,
                    rollback_error,
                )


def generate_keypairs(count: int) -> None:
    """Generates and stores multiple keypairs."""
    if os.path.exists(STATIC_KEYSTORE_PATH) and os.listdir(STATIC_KEYSTORE_PATH):
        logger.info(
            "Keypairs already exist in %s. Skipping generation.", STATIC_KEYSTORE_PATH
        )
        return

    os.makedirs(STATIC_KEYSTORE_PATH, exist_ok=True)

    for i in range(count):
        generate_keypair(i)

    logger.info("Successfully generated %d keypairs.", count)


def export_public_keys_to_file(file_path: str) -> None:
    """Exports all public keys to a specified JSON file."""
    try:
        dir_path = os.path.dirname(file_path)

        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        active_keypairs = StaticKeypairs.get_keypairs(status="active")

        public_keys = [
            {
                "kid": keypair.kid,
                "public_key": base64.b64encode(
                    x25519()
                    .deserialize(
                        decrypt_aes(
                            ENCRYPTION_KEY, keypair.keypair_bytes, is_bytes=True
                        )
                    )
                    .get_public_key()
                ).decode("utf-8"),
            }
            for keypair in active_keypairs
        ]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(public_keys, f, indent=2)

        logger.info("Public keys exported successfully to %s.", file_path)

    except Exception as e:
        logger.exception("Failed to export public keys: %s", e)
        raise


def test_keypairs() -> None:
    """Performs a key agreement test using two randomly selected keypairs."""
    try:
        keypairs = StaticKeypairs.get_keypairs(status="active")
        if len(keypairs) < 2:
            raise ValueError("Not enough keypairs for key agreement test.")

        keypair1, keypair2 = random.sample(keypairs, 2)

        keypair_1 = x25519().deserialize(
            decrypt_aes(ENCRYPTION_KEY, keypair1.keypair_bytes, is_bytes=True)
        )
        keypair_2 = x25519().deserialize(
            decrypt_aes(ENCRYPTION_KEY, keypair2.keypair_bytes, is_bytes=True)
        )

        shared_secret_1 = keypair_1.agree(keypair_2.get_public_key())
        shared_secret_2 = keypair_2.agree(keypair_1.get_public_key())

        if shared_secret_1 == shared_secret_2:
            logger.info("Key agreement successful: shared secret matches.")
        else:
            logger.error("Key agreement failed: shared secrets do not match.")

    except Exception as e:
        logger.exception("Key agreement test failed: %s", e)
        raise


def main() -> None:
    """CLI entry point for key management."""
    parser = argparse.ArgumentParser(description="x25519 Key Management CLI")
    subparser = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparser.add_parser("generate", help="Generate keypairs")
    generate_parser.add_argument(
        "-n", "--number", type=int, default=255, help="Number of keypairs to generate"
    )

    export_parser = subparser.add_parser("export", help="Export public keys")
    export_parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="static_x25519_pub_keys.json",
        help="Path to save the public keys file",
    )

    subparser.add_parser("test", help="Test key agreement")

    args = parser.parse_args()

    commands = {
        "generate": lambda: generate_keypairs(args.number),
        "export": lambda: export_public_keys_to_file(args.file),
        "test": test_keypairs,
    }

    commands[args.command]()


if __name__ == "__main__":
    main()
