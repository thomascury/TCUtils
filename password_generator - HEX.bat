@echo off
:loop
    python -m tcutils.password_generator -x
    pause
goto loop