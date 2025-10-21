from fastapi import APIRouter, HTTPException, Query
from pipetracker.core.config_loader import ConfigLoader
from pipetracker.core.log_scanner import LogScanner
from pipetracker.core.pattern_matcher import PatternMatcher
from pipetracker.core.trace_builder import TraceBuilder
from pipetracker.core.security import Security
from typing import List
from pydantic import BaseModel
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trace")


# Define Pydantic model for the trace record
class TraceRecord(BaseModel):
    timestamp: str
    service: str
    raw: str


@router.get("/{trace_id}")
async def get_trace(
    trace_id: str, config_path: str = Query(default="pipetracker.yaml")
) -> List[TraceRecord]:
    """Trace a record ID across logs.

    Args:
        trace_id: The ID to trace in the logs.
        config_path: Path to the configuration file (default: \
            pipetracker.yaml).

    Returns:
        A list of TraceRecord objects containing matched log entries.

    Raises:
        HTTPException: If the configuration file is not found (404),
                       invalid (400), or an internal error occurs (500).
    """
    try:
        conf = ConfigLoader().load(config_path)
        security = Security(conf.security.encrypt_logs)
        scanner = LogScanner(conf.log_sources, config=conf)
        files = scanner.scan()
        matcher = PatternMatcher(conf.match_keys)
        matches = []

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8") as fh:
                    for line in fh:
                        decrypted = security.decrypt_log(line)
                        processed_line = security.mask_pii(decrypted)
                        if matcher.match_line(processed_line, trace_id):
                            matches.append(
                                {
                                    "timestamp": matcher.extract_timestamp(
                                        processed_line
                                    ),
                                    "service": matcher.extract_service(
                                        processed_line
                                    ),
                                    "raw": processed_line.strip(),
                                }
                            )
            except (IOError, UnicodeDecodeError) as e:
                logger.error(f"Error processing {file_path}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing {file_path}: {str(e)}",
                )
            finally:
                if file_path.startswith(tempfile.gettempdir()):
                    try:
                        os.unlink(file_path)
                        logger.info(f"Deleted temporary file: {file_path}")
                    except (PermissionError, OSError) as e:
                        logger.warning(
                            f"Failed to delete temporary file {file_path}: {e}"
                        )

        if not matches:
            return []

        df = TraceBuilder().build(matches)
        df = df.rename(
            columns=lambda x: str(x)
        )  # Ensure all column names are strings
        records_dict = df.to_dict(orient="records")
        logger.debug(f"DataFrame records: {records_dict}")
        for record in records_dict:
            if not all(isinstance(key, str) for key in record.keys()):
                logger.warning(f"Non-string key found in record: {record}")
        records_dict = df.to_dict(orient="records")
        logger.debug(f"DataFrame records: {records_dict}")
        for record in records_dict:
            if not all(isinstance(key, str) for key in record.keys()):
                logger.warning(f"Non-string key found in record: {record}")

        records = [
            TraceRecord(**{str(k): v for k, v in record.items()})
            for record in records_dict
        ]
        return records

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.exception("Unexpected error during trace processing")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )
