from fastapi import APIRouter, HTTPException, Query
from pipetrack.core.config_loader import ConfigLoader
from pipetrack.core.log_scanner import LogScanner
from pipetrack.core.pattern_matcher import PatternMatcher
from pipetrack.core.trace_builder import TraceBuilder
from pipetrack.core.security import Security
import tempfile
import os

router = APIRouter(prefix="/trace")


@router.get("/{trace_id}")
async def get_trace(trace_id: str, config_path: str = Query("pipetrack.yaml")):
    """Trace a record ID across logs."""
    try:
        conf = ConfigLoader().load(config_path)
        security = Security(conf.security.encrypt_logs)
        scanner = LogScanner(conf.log_sources)
        files = scanner.scan()
        matcher = PatternMatcher(conf.match_keys)
        matches = []

        for file_path in files:
            try:
                with open(file_path) as fh:
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
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing {file_path}: {e}",
                )
            finally:
                if file_path.startswith(tempfile.gettempdir()):
                    try:
                        os.unlink(file_path)
                    except Exception:
                        pass

        df = TraceBuilder().build(matches)
        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
