@echo off
:loop
    python -m tcutils.password_generator -lun
    pause
goto loop