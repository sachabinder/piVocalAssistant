# Raspberry Pi Vocal Assistant

<a href="https://www.youtube.com/watch?v=8oKwM2E5yf4" target="_blank">
  <img src="https://img.youtube.com/vi/8oKwM2E5yf4/0.jpg" width="30%">
</a>
<a href="https://www.youtube.com/watch?v=vTR4IsfkEKc" target="_blank">
  <img src="https://img.youtube.com/vi/vTR4IsfkEKc/0.jpg" width="30%">
</a>
<a href="https://www.youtube.com/watch?v=vTR4IsfkEKc" target="_blank">
  <img src="https://img.youtube.com/vi/vTR4IsfkEKc/0.jpg" width="30%">
</a>

This project implements a personal voice assistant on a Raspberry Pi using Python. The assistant can listen to user commands, process them using [OpenAI's API](https://platform.openai.com/), make research on the internet using [Google Search API](https://serpapi.com/) and respond via text-to-speech. It supports wake and sleep words, and optional web search for enhanced query handling.

<p align="center">
  <img src="./figures/schematic1.png" alt="Schematic" width="600">
</p>

---

## Features

- **Speech Recognition**: Converts speech to text using [SpeechRecognition module](https://github.com/Uberi/speech_recognition).
- **Wake and Sleep Words**: Activates on hearing the wake word and deactivates with the sleep word or after a timeout and\or a keyword.
- **Text Processing**: Processes user queries using [OpenAI's API](https://platform.openai.com/) and eventually [Google Search API](https://serpapi.com/) and keeping conversation context.

<p align="center">
  <img src="./figures/querry_processing_schem.png" alt="Schematic" width="600">
  <img src="./figures/context_keeping_schem.png" alt="Schematic" width="600">
</p>

- **Text-to-Speech**: Converts text responses to speech using [Google Text-to-Speech (gTTS)](https://github.com/pndurette/gTTS).
- **LED Indicators**: Uses GPIO LEDs to indicate recording and playback states.
- **Customizable sound effects**: Play sound effects when the assistant is activated or deactivated.

---

## Requirements

### Hardware
- Raspberry Pi (tested on [Raspberry Pi zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) and [Raspberry Pi 4 2B 4Gb](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) ) 
- Raspberry Pi DAC hat [WM8960 Audio HAT](https://www.waveshare.com/wiki/WM8960_Audio_HAT)
- 2 LEDs connected to GPIO pins for recording and playback indication
- 2 resistors (220 Ohm) for the LEDs

### Software
- Python 3.11 or higher
- Virtual environment with the required Python packages
- Pip package manager

---

## Installation

### Prerequisites
Follow instruction to install your audio hat on your Raspberry Pi (WM8960 Audio HAT in this case) and test it!

Create a `.asoundrc` file in `/home/pi/` with the sound card you want to use:
```bash
pcm.!default {
    type hw
    card 1  # Replace with your desired card number
    device 0  # Replace with your desired device number
}

ctl.!default {
    type hw
    card 1  # Replace with your desired card number
}
``` 

### Step 1: Clone the Repository
```bash
git clone https://github.com/sachabinder/piVocalAssistant.git
```

### Step 2: Set Up a Virtual Environment
```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-venv
```

```bash
cd ~
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd piVocalAssistant
pip install -r requirements.txt
```

### Step 4: Install System Dependencies
```bash
sudo apt install portaudio19-dev python3-pyaudio flac espeak mpg123
```

---

## Environment Variables
Complete the [`.env`](./.env) file in the project directory by adding you API keys the following content:
```env
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

---

## Usage

### Running the Assistant
Activate the virtual environment and start the assistant:
```bash
source .venv/bin/activate
python main.py
```

### Wake and Sleep Words
- **Wake Word**: Say "Hey Assistant" to activate the assistant.
- **Sleep Word**: Say "Goodbye" to deactivate the assistant.

### LEDs
- **Recording LED**: Indicates when the assistant is listening.
- **Playback LED**: Indicates when the assistant is responding.

---

## Project Structure
```plaintext
src/piVocalAssistant/
├── main.py               # Main entry point for the assistant
├── speech2text.py        # Speech-to-text implementation
├── text_processing.py    # Query processing and LLM integration
├── text2speech.py        # Text-to-speech implementation
```

---

## Running on Boot
To automatically start the assistant on boot, follow these steps:

### Step 1: Made the Startup Script executable
```bash
chmod +x /home/pi/piVocalAssistant/run_service.sh
```

### Step 2: Create a systemd Service
```bash
sudo nano /etc/systemd/system/vocal_assistant.service
```
Add the following:
```ini
[Unit]
Description=Pi Vocal Assistant Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /home/pi/piVocalAssistant/run_service.sh
Restart=on-failure
RestartSec=5
WorkingDirectory=/home/pi/piVocalAssistant/
User=pi

[Install]
WantedBy=multi-user.target
```
Save and enable the service:
```bash
sudo systemctl enable vocal_assistant.service
sudo systemctl start vocal_assistant.service
```

### Step 3: Reboot and Test
Reboot the Raspberry Pi and check if the assistant starts automatically:
```bash
sudo reboot
```

---

## Troubleshooting

### Viewing Logs
- **System Logs**:
```bash
sudo journalctl -u vocal_assistant.service
```
- **Application Logs** (if redirected):
```bash
cat /home/pi/vocal_assistant.log
```

### Common Issues
- **Microphone Not Detected**: Ensure your microphone is properly connected and configured.
- **Dependencies Missing**: Reinstall missing Python or system packages.

---

## Contributing
Feel free to submit issues or pull requests to improve the project.