from fantasy_football_analyzer.sleeper import get_all_players
import os
import uuid
from datetime import datetime
from time import perf_counter
import logging
from dotenv import load_dotenv
from rich import print_json

logger = logging.getLogger(__name__)

# --- main ---
def main():
    run_id = uuid.uuid4()
    today = datetime.now().strftime("%Y-%m-%d")
    start = perf_counter()
    log_path = f"logs/{today}_league_data.log"
    run_status = "error"

    if not os.path.exists("logs"):
        os.mkdir("logs")

    logging.basicConfig(
        filename=log_path,
        filemode="a",
        level="DEBUG",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("requests_cache").setLevel(logging.WARNING)

    try:
        logger.info("===== RUN START: run_id=%s =====", run_id)
        load_dotenv()
        league_id = os.getenv("SLEEPER_LEAGUE_ID")

        if not league_id:
            raise SystemExit("SLEEPER_LEAGUE_ID is not set in .env")

        player = get_all_players("QB", True)
        print_json(data=player)

        run_status = "success"
    except Exception:
        logger.exception("Main failed to run")
        raise
    finally:
        end = perf_counter()
        runtime = end - start
        logger.info(
            "===== RUN END: run_id=%s duration=%s status=%s =====",
            run_id,
            str(round(runtime, 2)),
            run_status,
        )


if __name__ == "__main__":
    main()