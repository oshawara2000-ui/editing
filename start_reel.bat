@echo off
chcp 65001 >nul
REM Usage: start_reel.bat "C:\path\to\reel folder" [target_seconds] [reel|locked]
set "F=%~1"
set "T=%~2"
set "M=%~3"
if "%T%"=="" set T=45
if "%M%"=="" set M=reel
python "%~dp0scripts\probe.py" "%F%" || exit /b 1
python "%~dp0scripts\transcribe.py" "%F%" || exit /b 1
python "%~dp0scripts\gemini_fix.py" "%F%" || exit /b 1
python "%~dp0scripts\gemini_plan.py" "%F%" --target %T% --mode %M% || exit /b 1
python "%~dp0scripts\render_ffmpeg.py" "%F%" --draft || exit /b 1
echo.
echo Draft ready: %F%\_claude_preview\draft_720p_30fps.mp4
echo Review plan.json, set "approved": true, then: python "%~dp0scripts\render_ffmpeg.py" "%F%"
