import openai
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
logger = logging.getLogger(os.getenv("ASSISTANT_NAME", "Pi Assistant"))

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


def perform_web_search(query: str) -> dict:
    """Perform a web search using SerpApi to find the answer to the user's query.

    Args:
        query (str): The user's query.

    Returns:
        dict: The answer found from the web search.
    """
    logger.info("Making a web search to find the answer...")

    search = GoogleSearch(
        {
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "hl": os.getenv("PLAY_LANGUAGE", "en"),
            "gl": "fr",
        }
    )
    result = search.get_dict()

    if "answer_box" not in result:
        return "No answer box found"

    return result["answer_box"]


def is_web_search_required(query) -> bool:
    """Determine if a web search is required to answer the user's query.

    This is done by asking chat GPT if a web search is required for the given query.

    Args:
        query (str): The user's query.

    Returns:
        bool: True if a web search is required, False otherwise.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use "gpt-3.5-turbo" if you prefer
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond with 'True' if a web search is required to answer the user's query and 'False' otherwise. Provide no additional information.",
                },
                {"role": "user", "content": query},
            ],
        )
        # Extract and return the assistant's reply
        decision = response.model_dump()["choices"][0]["message"]["content"].strip()
        return decision.lower() == "true"
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


def process_query(
    query: str,
    conversation_history: list[dict],
    assistant_name: str = "Assistant",
    location: str = "Paris - France",
    allow_web_search: bool = True,
) -> list[dict]:
    """Process the user's query and generate a response.

    Args:
        query (str): The user's query.
        conversation_history (list): The conversation history.
        assistant_name (str, optional): The assistant's name. Defaults to "Assistant".
        location (str, optional): The assistant's location. Defaults to "Paris - France".
        allow_web_search (bool, optional): Whether to allow web search. Defaults to True.

    Returns:
        list: The updated conversation history.
    """
    if allow_web_search and is_web_search_required(query):
        web_search_result = perform_web_search(query)
        if web_search_result:
            query += (
                f"\n\nHere is some information from the web search: {web_search_result}"
            )

    if not conversation_history:
        conversation_history = [
            {
                "role": "system",
                "content": f"You are a helpful personal vocal assistant name {assistant_name}. \
                      Your location is {location}. The date is {datetime.now().strftime('%Y-%m-%d')} and \
                      the time is {datetime.now().strftime('%H:%M:%S')}. Respond to the user's query in a frendly way. \
                      Please make your response only of text (without any images, emojies and so on ...) \
                      Your response should be no longer than two sentences.",
            },
        ]

    conversation_history.append({"role": "user", "content": query})

    # Generate response using ChatGPT
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=conversation_history
        )
        conversation_history.append(
            {
                "role": "assistant",
                "content": response.model_dump()["choices"][0]["message"]["content"],
            }
        )
        return conversation_history
    except Exception as e:
        return f"An error occurred while processing your query: {e}"


if __name__ == "__main__":
    from utils import setup_logger

    logger = setup_logger(
        os.getenv("ASSISTANT_NAME", "Pi Assistant"),
        log_file=os.getenv("LOG_FILENAME", "assistant.log"),
        level=os.getenv("LOGGING_LEVEL", "INFO"),
    )

    logger.info("Welcome to your personal voice assistant! (Type 'exit' to quit)")
    conversation_history = []
    while True:
        user_query = input("You: ")
        if user_query.lower() == "exit":
            print("Goodbye!")
            break
        conversation_history = process_query(user_query, conversation_history)
        logger.info(f"Assistant: {conversation_history[-1]['content']}")
