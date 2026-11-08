import logging
import sys


def configure_logging(debug: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
        force=True,
    )
    # Bibliotecas muito verbosas em DEBUG.
    for noisy in ("pymongo", "asyncio", "multipart"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
