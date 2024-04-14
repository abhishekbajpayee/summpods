import openai
import urllib3
import uuid
import os
import logging
import math
import pydub
from src.lib.utils import (
    KEYS,
    get_transcription_if_exists,
)
from src.lib.models import (
    Transcription,
    TranscriptionModel,
)

openai.api_key = KEYS["OPENAI_KEY"]

logger = logging.getLogger(__name__)


def get_audio_splits(file_path):
    """
    Generates a list of audio splits from the given file path, splitting 
        the file if its size exceeds the maximum file size.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        List[str]: A list of file paths representing the audio splits.

    Notes:
        - If the file size is below the maximum file size, the function returns a 
            list containing the original file path.
        - The maximum file size is set to 26,214,400 (25MB) bytes.
    """
    file_size = os.path.getsize(file_path)
    MAX_FILE_SIZE = 26214400
    if file_size < MAX_FILE_SIZE:
        return [file_path]

    logger.debug("File size above 25MB, splitting file...")
    src_audio = pydub.AudioSegment.from_file(file_path)
    duration_seconds = src_audio.duration_seconds
    num_splits = math.ceil(file_size / (MAX_FILE_SIZE * 0.99))
    logger.info(num_splits)
    logger.info(duration_seconds)

    duration_milliseconds = duration_seconds * 1000
    split_duration_milliseconds = int(duration_milliseconds / num_splits)
    audio_slices = src_audio[::split_duration_milliseconds]

    slice_filenames = []
    for audio_slice in audio_slices:
        if len(audio_slice) < 1000:
            logger.debug("Slice size < 1s, skipping")
            continue
        slice_filename_prefix = file_path.split(".")[0]
        slice_filename = "{prefix}_{i}.mp3".format(prefix=slice_filename_prefix, i=len(slice_filenames))
        audio_slice.export(slice_filename, format="mp3")
        slice_filenames.append(slice_filename)

    return slice_filenames


def transcribe_files(audio_files):
    """
    Transcribes a list of audio files.

    Args:
        audio_files (List[str]): A list of paths to audio files to be transcribed.

    Returns:
        str: The concatenated transcription result from all the audio files.

    TODO:
        - Improve the joining logic to handle lost words and broken sentences.
          Explore overlapping audio chunks for smarter joining.
    """
    logger.debug("Transcribing files...")
    split_transcriptions = []
    for audio_file in audio_files:
        with open(audio_file, "rb") as f:
            transcription_result = openai.Audio.transcribe("whisper-1", f)
            logger.debug(transcription_result)
            split_transcriptions.append(transcription_result)

    transcription_result = ''
    logger.debug("Joining transcription results...")
    for transcription_chunk in split_transcriptions:
        logger.debug(transcription_chunk["text"])
        transcription_result += transcription_chunk["text"]

    return transcription_result


# function to transcribe an audio file using whisper API
def transcribe(episode, model=TranscriptionModel(name="whisper")):
    """
    Transcribes the given episode using the specified transcription model.

    Args:
        episode (Episode): The episode to transcribe.
        model (TranscriptionModel, optional): The transcription model to use.
            Defaults to TranscriptionModel(name="whisper").

    Returns:
        Transcription: The transcription of the episode.

    Raises:
        Exception: If the specified model is not supported for transcription.

    Example:
        transcribe(episode, model=TranscriptionModel(name="whisper"))

    Notes:
        - Only the "whisper" model is supported for transcription.
        - The episode audio file will be downloaded and transcribed.
        - The downloaded / generated file(s) will be deleted after transcription.
        - Assumption that download file extension can always be mp3
    """
    if model.name != "whisper":
        raise Exception("Only whisper model is supported right now for transcription")

    if episode is None:
        raise ValueError("Episode cannot be None")

    if (transcription := get_transcription_if_exists(episode, model)):
        return transcription

    logger.debug("Generating transcription for episode...")
    http = urllib3.PoolManager()
    response = http.request('GET', episode.audioUrl)

    # download file to random filename
    # TODO: does this need an extension at all?
    tmp_filename = "{uuid}.mp3".format(uuid=str(uuid.uuid4()))
    logger.debug("Downloading {src} to {dst}...".format(src=episode.audioUrl, dst=tmp_filename))
    with open(tmp_filename, 'wb') as downloaded_file:
        downloaded_file.write(response.data)

    # get file splits if file needs to be split
    audio_splits = get_audio_splits(tmp_filename)

    # transcribe all splits
    transcription_result = transcribe_files(audio_splits)

    # delete downloadeded / generated file
    logger.debug("Deleting files...")
    audio_splits += [tmp_filename]
    for filename in audio_splits:
        logger.debug(filename)
        os.remove(filename)

    transcription = Transcription(
        episode=episode,
        transcription_model=model,
        text=transcription_result
    )
    logger.debug("Saving transcription...")
    transcription.save(cascade=True)
    return transcription
