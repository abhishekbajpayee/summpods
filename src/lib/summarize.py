import openai
import logging
import tiktoken
from src.lib.utils import (
    KEYS,
    get_summary_if_exists,
)
from src.lib.models import (
    SummarizationModel,
    Summary,
)
from src.lib import transcribe

openai.api_key = KEYS["OPENAI_KEY"]

logger = logging.getLogger(__name__)

PROMPTS = {
    "generic_summarize": ("You are a highly skilled AI trained in language comprehension and summarization. "
                          "I would like you to read the following text and summarize it into a concise abstract paragraph. "
                          "Aim to retain the most important points, providing a coherent and readable summary that could help a person "
                          "understand the main points of the discussion without needing to read the entire text. "
                          "Please avoid unnecessary details or tangential points. Please also formatthe output in markdown."),
}


def summarize(transcription, model=SummarizationModel(name="gpt-3.5-turbo")):
    """
    Generate a summary of a transcription using a specified summarization model.

    Args:
        transcription (Transcription): The transcription object to be summarized.
        model (SummarizationModel, optional): The summarization model to be used.
            Defaults to SummarizationModel(name="gpt-3.5-turbo").

    Returns:
        Summary: The generated summary of the transcription.

    Raises:
        ValueError: If transcription is None.
    """
    if transcription is None:
        raise ValueError("Transcription cannot be None")

    prompt = PROMPTS["generic_summarize"]
    if (summary := get_summary_if_exists(transcription, model, prompt)):
        return summary

    # check number of tokens in transcription here
    MAX_TOKEN_COUNT = 4096
    encoding = tiktoken.encoding_for_model(model.name)
    token_count = len(encoding.encode(transcription.text))
    if token_count > MAX_TOKEN_COUNT:
        raise ValueError("Transcription has {token_count} tokens, "
                         "which is above the maximum token count!".format(token_count=token_count))

    logger.debug("Generating summary for transcription...")
    response = openai.ChatCompletion.create(
        model=model.name,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": transcription.text
            }
        ]
    )
    logger.debug(response)

    summary = Summary(
        transcription=transcription,
        summarization_model=model,
        prompt=prompt,
        text=response['choices'][0]['message']['content']
    )
    logger.debug("Saving summary...")
    summary.save(cascade=True)
    return summary


def transcribe_and_summarize(episode):
    """
    Generate a summary of the given episode by transcribing it and summarizing the transcription.

    Args:
        episode (str): The episode to be transcribed and summarized.

    Returns:
        str: The summary of the episode.
    """
    transcription = transcribe.transcribe(episode)
    summary = summarize(transcription)
    return summary
