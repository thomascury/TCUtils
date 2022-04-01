@echo off
venv\Scripts\activate.bat
:loop
    python -m tcutils.diceware_passphrase
    pause
goto loop