#!/bin/bash
source /home/pi/.venv/bin/activate
cd /home/pi/piVocalAssistant/
python src/PiVocalAssistant/main.py >&1
