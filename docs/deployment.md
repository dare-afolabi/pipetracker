# Deployment

Deployment guide for Pipetracker.

## Prerequisites
- Python 3.9+
- Dependencies installed
- Valid `pipetracker.yaml`

## CLI Deployment
Run directly:
```bash
pipetracker trace TXN12345 --config /path/to/pipetracker.yaml
```

Schedule using cron or Lambda for automation.

## API Deployment
Start FastAPI server:
```bash
uvicorn pipetracker.api.main:app --host 0.0.0.0 --port 8000
```

Use a process manager like `supervisord` or containerize using Docker for production.

## Logging

- **Configure Logging**: Use a `logging.conf` file for standardized logging settings:
```bash
  [loggers]
  keys=root,pipetracker
  [handlers]
  keys=console,file
  [formatters]
  keys=simple
  [logger_root]
  level=INFO
  handlers=console
  [logger_pipetracker]
  level=INFO
  handlers=console,file
  qualname=pipetracker
  propagate=0
  [handler_console]
  class=StreamHandler
  level=INFO
  formatter=simple
  args=(sys.stdout,)
  [handler_file]
  class=FileHandler
  level=INFO
  formatter=simple
  args=('pipetracker.log', 'a')
  [formatter_simple]
  format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Place this in the project root and adjust `level` or add rotation as needed. Forward logs to a service like CloudWatch or ELK Stack for centralized monitoring.

*Generated on October 21, 2025*