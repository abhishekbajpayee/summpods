import openai
import urllib3
import uuid
import os
import logging
from src.utils import KEYS
from src.models import (
    Transcription,
    TranscriptionModel,
    Episode,
)

openai.api_key = KEYS["OPENAI_KEY"]

logger = logging.getLogger(__name__)


def get_transcription_if_exists(episode, transcription_model):
    """
    Get the transcription if it exists for the given episode and transcription
        model.

    Args:
        episode (Episode): The episode object.
        transcription_model (TranscriptionModel): The transcription model
            object.

    Returns:
        Transcription or False: The transcription object if it exists,
            otherwise False.
    """
    episode = Episode.objects(uuid=episode.uuid)
    if episode:
        logger.debug("Episode exists")
        if len(episode) > 1:
            logger.error("Multiple episodes found with same uuid!")
    else:
        return False
    transcription_model = \
        TranscriptionModel.objects(name=transcription_model.name)
    if transcription_model:
        logger.debug("Transcription model exists")
        if len(transcription_model) > 1:
            logger.error("Multiple transcription models found with same name!")
    else:
        return False
    transcription = Transcription.objects(
        episode=episode[0],
        transcription_model=transcription_model[0]
    )
    if transcription:
        logger.debug("Transcription exists")
        if len(transcription) > 1:
            logger.error("Multiple transcriptions found with same episode \
                         and model!")
        return transcription[0]
    else:
        return False


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
        - The downloaded file will be deleted after transcription.
        - Assumption that download file extension can always be mp3
    """
    if model.name != "whisper":
        raise Exception("Only whisper model is supported right now \
                        for transcription")

    transcription = get_transcription_if_exists(episode, model)
    if transcription:
        return transcription

    logger.debug("Generating transcription for episode...")
    http = urllib3.PoolManager()
    response = http.request('GET', episode.audioUrl)

    # download file to random filename
    # TODO: does this need an extension at all?
    tmp_filename = "{uuid}.mp3".format(uuid=str(uuid.uuid4()))
    logger.debug("Downloading {src} to {dst}...".format(src=episode.audioUrl,
                                                        dst=tmp_filename))
    with open(tmp_filename, 'wb') as downloaded_file:
        downloaded_file.write(response.data)

    logger.debug("Transcribing file...")
    with open(tmp_filename, "rb") as f:
        transcription_result = openai.Audio.transcribe("whisper-1", f)
        logger.debug(transcription_result)

    # delete downloaded file
    logger.debug("Deleting file {}...".format(tmp_filename))
    os.remove(tmp_filename)

    transcription = Transcription(
        episode=episode,
        transcription_model=model,
        text=transcription_result["text"]
    )
    transcription.save(cascade=True)
    return transcription
