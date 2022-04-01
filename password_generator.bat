@echo off
:loop
    venv\Scripts\python -m tcutils.password_generator
    pause
goto loop