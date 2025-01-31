import os
import logging
import sounddevice 
import speech_recognition as sr

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(os.getenv("ASSISTANT_NAME", "Pi Assistant"))

rec = sr.Recognizer()
mic = sr.Microphone()

rec.dynamic_energy_threshold = False
rec.energy_threshold = 400


def speech_to_text(adapt_duration=0.5, language="en-EN", timeout=10):
    """Converts speech to text using google's speech recognition.

    Parameters
    ----------
    adapt_duration : float
        The duration of the adaptation phase. Default is 0.5.
    language : str
        The language of the speech. Default is "en-EN".
    timeout : int
        The maximum time to wait for the speech. Default is 10.

    Returns
    -------
    str
        The text of the speech.
    """
    logger.debug("Listening for speech...")
    with mic as source:
        rec.adjust_for_ambient_noise(source, duration=adapt_duration)
        audio = rec.listen(source, timeout=timeout)
    return rec.recognize_google(audio, language=language)


if __name__ == "__main__":
    # Live transcribe the speech
    from utils import setup_logger

    logger = setup_logger(
        os.getenv("ASSISTANT_NAME", "Pi Assistant"),
        log_file=os.getenv("LOG_FILENAME", "assistant.log"),
        level=os.getenv("LOGGING_LEVEL", "INFO"),
    )

    while True:
        try:
            text = speech_to_text()
            logger.info(text)
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            logger.error("Could not understand the audio")
        except sr.RequestError as e:
            logger.error(f"Could not request results; {e}")
        except KeyboardInterrupt:
            break
