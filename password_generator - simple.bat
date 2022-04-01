@echo off
:loop
    venv\Scripts\python -m tcutils.password_generator -lun
    pause
goto loop