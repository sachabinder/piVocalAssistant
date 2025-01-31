import os
import sys
from dotenv import load_dotenv

script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(script_path))
sys.path.append(project_root)
load_dotenv()

from PiVocalAssistant.utils import setup_logger

# Logger configuration
logger = setup_logger(
    os.getenv("ASSISTANT_NAME", "Pi Assistant"),
    log_file=os.getenv("LOG_FILENAME", "assistant.log"),
    level=os.getenv("LOGGING_LEVEL", "INFO"),
)

logger.info("Assistant is starting...")

import speech_recognition as sr
from gpiozero import LED



from PiVocalAssistant.speech2text import speech_to_text
from PiVocalAssistant.text_processing import process_query
from PiVocalAssistant.text2speech import text_to_speech


# LED
REC_LED = LED(os.environ.get("REC_LED_PIN", 24))
PLAY_LED = LED(os.environ.get("PLAY_LED_PIN", 25))
WAKE_WORD = os.environ.get("WAKE_WORD", "hey assistant")
SLEEP_WORD = os.environ.get("SLEEP_WORD", "goodbye")

logger.debug(f"Recording LED initialized on pin {REC_LED}")
logger.debug(f"Playing LED initialized on pin {PLAY_LED}")
logger.info(f"Wake word is: {WAKE_WORD}")
logger.info(f"Sleep word is: {SLEEP_WORD}")

def main():
    conversation_history = []
    is_awake = False

    while True:
        try:
            if is_awake:
                os.system(f'mpg123 sounds/sound1.mp3 >/dev/null 2>&1 &')
                REC_LED.on()

            user_query = speech_to_text(
                adapt_duration=float(os.environ.get("REC_ADAPT_DURATION", 0.5)),
                language=os.environ.get("REC_LANGUAGE", "en-US"),
                timeout=int(os.environ.get("REC_TIMEOUT", 10)),
            )

            logger.debug(f"User default query: {user_query}")

            if user_query:
                # Check for wake word to activate the assistant
                if not is_awake and WAKE_WORD.lower() in user_query.lower():
                    logger.info("Assistant is activated")
                    REC_LED.on()
                    is_awake = True
                    continue

                # If awake, process the query
                if is_awake:
                    # Check for sleep word to deactivate the assistant
                    if SLEEP_WORD.lower() in user_query.lower():
                        logger.info("Assistant is deactivated")
                        is_awake = False
                        os.system(f'mpg123 sounds/sound2.mp3 >/dev/null 2>&1 &')
                        REC_LED.off()
                        continue

                    logger.info(f"User: {user_query}")
                    os.system(f'mpg123 sounds/sound3.mp3 >/dev/null 2>&1 &')

                    # Process the user's query
                    REC_LED.off()
                    conversation_history = process_query(
                        user_query,
                        conversation_history,
                        assistant_name=os.getenv("ASSISTANT_NAME", "Assistant"),
                    )
                    assistant_response = conversation_history[-1]["content"]
                    PLAY_LED.on()
                    logger.info(f"Assistant: {assistant_response}")
                    text_to_speech(
                        assistant_response,
                        language=os.environ.get("PLAY_LANGUAGE", "en"),
                        tld=os.environ.get("PLAY_REGION", "us"),
                    )
                    PLAY_LED.off()

        except sr.WaitTimeoutError:
            if is_awake:
                REC_LED.off()
                is_awake = False
                os.system(f'mpg123 sounds/sound2.mp3 >/dev/null 2>&1 &')
                continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            logger.error(f"Could not request results; {e}")
        except KeyboardInterrupt:
            REC_LED.off()
            PLAY_LED.off()
            break


if __name__ == "__main__":
    REC_LED.off()
    PLAY_LED.off()
    logger.info("Assistant is ready to assist you!")
    main()
    logger.info("Assistant is shutting down...")
