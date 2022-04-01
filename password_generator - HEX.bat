@echo off
:loop
    venv\Scripts\python -m tcutils.password_generator -x
    pause
goto loop