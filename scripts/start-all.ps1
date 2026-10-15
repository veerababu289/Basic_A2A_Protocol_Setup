# Run from project root in a PowerShell terminal after activating .venv.
# Opens each service in a new terminal window.
Start-Process powershell -ArgumentList '-NoExit','-Command','.\.venv\Scripts\Activate.ps1; uvicorn agents.order_agent:app --host 127.0.0.1 --port 8001'
Start-Process powershell -ArgumentList '-NoExit','-Command','.\.venv\Scripts\Activate.ps1; uvicorn agents.payment_agent:app --host 127.0.0.1 --port 8002'
Start-Process powershell -ArgumentList '-NoExit','-Command','.\.venv\Scripts\Activate.ps1; adk web coordinator --port 8000'
