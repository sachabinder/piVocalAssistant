import os
import logging
import tempfile
from dotenv import load_dotenv
from io import BytesIO
from gtts import gTTS
from utils import get_unique_filename

load_dotenv()

logger = logging.getLogger(os.getenv("ASSISTANT_NAME", "Pi Assistant"))


def text_to_speech(text, language="en", tld="us", file_path=None):
    """Convert text to speech using gTTS and optionally return audio data.

    Parameters
    ----------
    text : str
        The text to convert to speech.
    language : str
        The language of the speech. Default is "en".
    tld : str
        The top level domain of the speech. Default is "us".
    """
    mp3file = BytesIO()
    tts = gTTS(text, lang=language, tld=tld)
    tts.write_to_fp(mp3file)
    mp3file.seek(0)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_mp3:
        logger.info(f"writting to mp3 temp file {temp_mp3.name}")
        temp_mp3.write(mp3file.read())  # Write the mp3 data to the temp file
        temp_mp3.flush()  # Ensure data is written to disk
        temp_mp3_path = temp_mp3.name
        logger.debug(f"Playing the following text: {text}")
        os.system(f"mpg123 {temp_mp3_path} >/dev/null 2>&1")  # Redirect stdout and stderr
    
    # Save MP3 if file_path is provided
    if file_path:
        unique_file_path = get_unique_filename(file_path)  # Get a unique filename
        try:
            with open(unique_file_path, "wb") as output_mp3:
                output_mp3.write(mp3file.getvalue())  # Save MP3 data to file
            logger.info(f"MP3 file saved at: {unique_file_path}")
        except Exception as e:
            logger.error(f"Error saving MP3 file: {e}")



if __name__ == "__main__":
    while True:
        text = input("Enter text to convert to speech: ")
        text_to_speech(text)