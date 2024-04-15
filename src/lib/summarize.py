import openai
import logging
import math
import re
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
    "generic_summarize":
        ("You are a highly skilled AI trained in language comprehension and summarization. "
         "I would like you to read the following text and summarize it into a concise abstract paragraph. "
         "Aim to retain the most important points, providing a coherent and readable summary that could help a person "
         "understand the main points of the discussion without needing to read the entire text. "
         "Please avoid unnecessary details or tangential points. Please also format the output in markdown."),
    "extract_key_points":
        ("I would like you to read the following text and extract the overall background of what is being discussed "
         "and generate a list of key points. Aim to extract content that could later help a person summarize the "
         "original text."),
    "chunk_summary":
        ("In under {N} words, I would like you to read the following text and summarize the overall topics "
         "being discussed within a few paragraphs."),
    "joined_summarize":
        ("I would like you to summarize the following transcription of a podcast, which describes various topics "
         "discussed in it, into a concise abstract paragraph. Aim to retain the most important points, providing a "
         "coherent and readable summary that could help a person understand the main points of the discussion "
         "without needing to read the entire text. Also exclude sponsored mentions or advertisements from summary. "
         "Please also format the output in markdown"),
}

MAX_TOKEN_COUNT = 4096

# parameters to tune length of chunks and chunk summaries
_chunk_split_safety_factor = 0.9
_chunk_overlap_ratio = 0.05
_chunk_summary_word_limit_safety_factor = 0.9


def get_token_count(text, model):
    """
    Returns the number of tokens in the given text using the specified model.

    Parameters:
        text (str): The input text to count the tokens from.
        model (Model): The model to use for token encoding.

    Returns:
        int: The number of tokens in the text.
    """
    return len(tiktoken.encoding_for_model(model.name).encode(text))


def get_prompt_response(prompt, text, model):
    """
    Generates a response using OpenAI's Chat Completion API.

    Args:
        prompt (str): The system prompt for the conversation.
        text (str): The user's message in the conversation.
        model (str): The name of the OpenAI model to use.

    Returns:
        str: The response generated by the Chat Completion API.
    """
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
                "content": text
            }
        ]
    )
    logger.debug(response)
    return response['choices'][0]['message']['content']


def get_chunk_indices(text, model):
    """
    Calculates the indices for splitting a text into chunks for processing.

    Args:
        text (str): The input text.
        model (str): The model to be used for transcription (determines tokenization scheme).

    Returns:
        list: A list of tuples representing the start and end indices of each chunk.
    """
    # check number of tokens in transcription
    token_count = get_token_count(text, model)

    # number of chunks to split into
    num_chunks = math.ceil(token_count / (MAX_TOKEN_COUNT * _chunk_split_safety_factor))
    logger.debug("Number of chunks: {num_chunks}".format(num_chunks=num_chunks))

    # calculate chunk length and overlap
    transcription_length = len(text)
    logger.debug("Transcription length: {transcription_length}".format(transcription_length=transcription_length))
    chunk_length = int(
        transcription_length / (
            2 * (1 - _chunk_overlap_ratio) +
            _chunk_overlap_ratio * (num_chunks - 1) +
            (1 - 2 * _chunk_overlap_ratio) * max(0, num_chunks - 2)
        )
    )
    chunk_overlap = int(chunk_length * _chunk_overlap_ratio)
    logger.debug("Chunk length: {chunk_length}".format(chunk_length=chunk_length))
    logger.debug("Chunk overlap: {chunk_overlap}".format(chunk_overlap=chunk_overlap))

    chunk_indices = []
    for i in range(num_chunks):
        start = max(0, (i * chunk_length) - (chunk_overlap))
        end = start + chunk_length
        # if last chunk, index to end
        if (i == num_chunks - 1):
            end = transcription_length
        chunk_indices.append((start, end))

    return chunk_indices


def sanitize_and_join_summary_texts(chunk_summary_texts):
    """
    Generates a sanitized and joined summary text from a list of detailed chunk summary
    texts. The joined text output from this function is used to generate the final short
    summary of the entire text.

    :param chunk_summary_texts: A list of chunk summary texts.
    :type chunk_summary_texts: list[str]

    :return: The joined summary text.
    :rtype: str
    """
    joined_summary_text = ""
    for i, chunk_summary_text in enumerate(chunk_summary_texts):
        replace = ("The overall topics", "Additional topics")
        if i > 0:
            if chunk_summary_text[:len(replace[0])] == replace[0]:
                chunk_summary_text = replace[1] + chunk_summary_text[len(replace[0]):]
            if joined_summary_text[-1] != " ":
                joined_summary_text += " "
        joined_summary_text += chunk_summary_text

    logger.debug(joined_summary_text)
    return joined_summary_text


def chunk_and_summarize(transcription, model):
    """
    Generates a summary by breaking up the given transcription into chunks. Each chunk is
    summarized first in some detail. The detailed summaries for each chunk are then joined
    and the joined text is used to generate the final summary.

    Args:
        transcription (str): The full transcription text.
        model (str): The name of the model to use for generating summaries.

    Returns:
        str: The generated summary text.

    Raises:
        Exception: If the generated summary exceeds the maximum token count.
    """
    logger.info("Generating summary by breaking up transcription into chunks...")

    # get chunk indices
    chunk_indices = get_chunk_indices(transcription.text, model)

    # extract topic summaries from chunks
    chunk_summary_texts = []
    for i, (start, end) in enumerate(chunk_indices):
        logger.debug("Chunk {i}/{N}".format(i=i + 1, N=len(chunk_indices)))
        logger.debug("start:end: {start}:{end}".format(start=start, end=end))
        chunk = transcription.text[start:end]
        chunk_token_count = get_token_count(chunk, model)
        logger.debug("Chunk token count: {chunk_token_count}".format(chunk_token_count=chunk_token_count))
        # create prompt with appropriate word count
        chunk_summary_word_limit = int(MAX_TOKEN_COUNT * _chunk_summary_word_limit_safety_factor / len(chunk_indices))
        prompt = PROMPTS["chunk_summary"].format(N=chunk_summary_word_limit)

        # sanitize chunk in basic way to remove dangling sentences otherwise gpt-3.5-turbo
        # seems to generate hallucinated completions
        sentence_starts = [m.start() for m in re.finditer(r"\. ", chunk)]
        # remove dangling sentence at the end of chunk
        if len(sentence_starts) > 0:
            chunk = chunk[:sentence_starts[-1] + 1]
            # if not first chunk, remove dangling sentence at the start
            if i > 0:
                chunk = chunk[sentence_starts[0] + 2:]
        else:
            logger.warning("No sentences found in chunk which is odd.")

        chunk_summary_text = get_prompt_response(prompt, chunk, model)
        chunk_summary_token_count = get_token_count(chunk_summary_text, model)
        logger.debug("Chunk summary token count: {chunk_summary_token_count}".format(chunk_summary_token_count=chunk_summary_token_count))
        chunk_summary_texts.append(chunk_summary_text)

    # sanitize and join summary texts
    joined_summary_text = sanitize_and_join_summary_texts(chunk_summary_texts)
    joined_summary_token_count = get_token_count(joined_summary_text, model)
    logger.debug("Joined summary token count: {joined_summary_token_count}".format(joined_summary_token_count=joined_summary_token_count))

    if joined_summary_token_count > MAX_TOKEN_COUNT:
        raise Exception("Joined summary exceeds maximum token count!")

    # re-summarize joined summary texts for final summary
    summary_text = get_prompt_response(PROMPTS["joined_summarize"], joined_summary_text, model)
    return summary_text


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

    # check number of tokens in transcription here
    encoding = tiktoken.encoding_for_model(model.name)
    token_count = len(encoding.encode(transcription.text))
    logger.debug("Token count: {token_count}".format(token_count=token_count))

    prompt = PROMPTS["generic_summarize"]
    if token_count > MAX_TOKEN_COUNT:
        # if token_count exceeds MAX_TOKEN_COUNT, it is implied that the prompt for summarizing
        # joined chunks is used for the purpose of caching
        # TODO: this is not very smart but it works for now
        prompt = PROMPTS["joined_summarize"]

    if (summary := get_summary_if_exists(transcription, model, prompt)):
        return summary

    if token_count > MAX_TOKEN_COUNT:
        # chunk transcription and generate summary
        summary_text = chunk_and_summarize(transcription, model)
    else:
        logger.info("Generating summary for transcription in one shot...")
        summary_text = get_prompt_response(prompt, transcription.text, model)

    summary = Summary(
        transcription=transcription,
        summarization_model=model,
        prompt=prompt,
        text=summary_text
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
