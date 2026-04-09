@echo off
cd /d "%~dp0"
for /f "tokens=1,* delims==" %%A in (.env) do (
    if "%%A"=="ANTHROPIC_API_KEY" set ANTHROPIC_API_KEY=%%B
)
echo Starting BRHS Chatbot server...
echo Open http://localhost:8000/static/widget.html in your browser.
"%LOCALAPPDATA%\Programs\Thonny\python.exe" -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
