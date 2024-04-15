import logging
import yaml
from src.lib.models import (
    Episode,
    Transcription,
    TranscriptionModel,
    SummarizationModel,
    Summary,
)

logger = logging.getLogger(__name__)

# load yaml file with API keys
KEYS = None
with open("/.secrets/keys", "r") as f:
    KEYS = yaml.safe_load(f)

if KEYS is None:
    raise Exception("Could not load secrets file!")


def get_episode_if_exists(uuid):
    """
    Retrieve an episode if it exists in the database.

    Args:
        uuid (str): The UUID of the episode to retrieve.

    Returns:
        Episode or None: The episode object if it exists in the database, None otherwise.
    """
    episode = Episode.objects(uuid=uuid)
    if episode:
        logger.debug("Episode exists")
        if len(episode) > 1:
            logger.error("Multiple episodes found with same uuid!")
        return episode[0]
    else:
        return None


def get_transcription_model_if_exists(name):
    """
    Retrieve a transcription model if it exists in the database.

    Parameters:
        name (str): The name of the transcription model.

    Returns:
        TranscriptionModel or None: The retrieved transcription model if it exists, 
        otherwise None.
    """
    transcription_model = TranscriptionModel.objects(name=name)
    if transcription_model:
        logger.debug("Transcription model exists")
        if len(transcription_model) > 1:
            logger.error("Multiple transcription models found with same name!")
        return transcription_model[0]
    else:
        return None


def get_transcription_if_exists(episode, transcription_model):
    """
    Returns the transcription object if it exists for the given episode and transcription model.

    Parameters:
        episode (Episode): The episode object.
        transcription_model (TranscriptionModel): The transcription model object.

    Returns:
        Transcription or None: The transcription object if it exists, otherwise None.
    """
    if (episode := get_episode_if_exists(episode.uuid)) is None:
        return None
    if (transcription_model := get_transcription_model_if_exists(
            transcription_model.name)) is None:
        return None
    if (transcription := Transcription.objects(
            episode=episode, transcription_model=transcription_model)):
        logger.debug("Transcription exists")
        if len(transcription) > 1:
            logger.error("Multiple transcriptions found with same episode \
                          and model!")
        return transcription[0]
    else:
        return None


def get_summarization_model_if_exists(name):
    """
    Retrieves a summarization model from the database if it exists.

    Parameters:
        name (str): The name of the summarization model to retrieve.

    Returns:
        SummarizationModel or None: The matching summarization model object if found, 
                                   otherwise None.
    """
    summarization_model = SummarizationModel.objects(name=name)
    if summarization_model:
        logger.debug("Summarization model exists")
        if len(summarization_model) > 1:
            logger.error("Multiple summarization models found with same name!")
        return summarization_model[0]
    else:
        return None


def get_summary_if_exists(transcription, summarization_model, prompt):
    """
    Check if a summary exists for a given transcription, summarization model, and prompt.
    
    Args:
        transcription (str): The transcription text.
        summarization_model (SummarizationModel): The summarization model object.
        prompt (str): The prompt for summarization.
    
    Returns:
        Summary or None: The summary object if it exists, otherwise None.
    """
    if (summarization_model := get_summarization_model_if_exists(
            summarization_model.name)) is None:
        return None
    if (summary := Summary.objects(
            transcription=transcription,
            summarization_model=summarization_model,
            prompt=prompt)):
        logger.debug("Summary exists")
        if len(summary) > 1:
            logger.error("Multiple summaries found with same transcription \
                          and model!")
        return summary[0]
    else:
        return None
