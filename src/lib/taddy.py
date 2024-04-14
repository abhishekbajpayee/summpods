import requests
import logging
from src.lib.utils import (
    KEYS,
    get_episode_if_exists
)
from src.lib.models import (
    Podcast,
    Episode,
)

HEADERS = {
    "X-USER-ID": KEYS["TADDY_USER_ID"],
    "X-API-KEY": KEYS["TADDY_KEY"],
}

ENDPOINT = "https://api.taddy.org"

logger = logging.getLogger(__name__)


def handle_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(response.status_code)
        return False


def search_or_get_podcast(term=None, uuid=None):
    """
    A function that searches for a podcast by term or gets a podcast by UUID.

    Parameters:
        term (str): The search term to find a podcast. Default is None.
        uuid (str): The UUID of the podcast to get. Default is None.

    Returns:
        podcast (Podcast): An instance of the Podcast class representing the podcast
            that was found or None if no podcast is found.
    """
    if term is None and uuid is None:
        logger.error("You must provide a search term or a podcast uuid!")
        return False
    if uuid:
        logger.debug("Getting podcast: {uuid}".format(uuid=uuid))
        query = """
        query {{
            getPodcastSeries(uuid:"{uuid}"){{
                uuid
                name
                itunesId
                description
                imageUrl
                totalEpisodesCount
            }}
        }}
        """.format(uuid=uuid)
    else:
        logger.debug("Searching for podcast: {term}".format(term=term))
        query = """
        query {{
            getPodcastSeries(name:"{term}"){{
                uuid
                name
                itunesId
                description
                imageUrl
                totalEpisodesCount
            }}
        }}
        """.format(term=term)
    response = requests.post(
        url=ENDPOINT,
        json={"query": query},
        headers=HEADERS
    )
    response_json = handle_response(response)
    podcast_json = response_json["data"]["getPodcastSeries"]
    logger.debug(podcast_json)
    podcast = Podcast(
        name=podcast_json["name"],
        uuid=podcast_json["uuid"],
        description=podcast_json["description"],
        itunesId=str(podcast_json["itunesId"]),
        imageUrl=podcast_json["imageUrl"],
        episodeCount=podcast_json["totalEpisodesCount"],
    )
    return podcast


def get_episodes(podcast, page=1, limitPerPage=10):
    """
    Retrieves episodes for a given podcast.

    Args:
        podcast (Podcast): The podcast object for which to retrieve episodes.
        page (int, optional): The page number of the episodes to retrieve. Defaults to 1.
        limitPerPage (int, optional): The maximum number of episodes per page. Defaults to 10.

    Returns:
        List[Episode]: A list of Episode objects representing the retrieved episodes.
    """
    logger.debug(
        "Getting episodes for podcast: {uuid} ({name})".format(
            uuid=podcast.uuid,
            name=podcast.name
        )
    )
    query = """
    query {{
        getPodcastSeries(uuid:"{uuid}"){{
            uuid
            name
            episodes(page:{page},limitPerPage:{limitPerPage}){{
                uuid
                name
                description
                audioUrl
            }}
        }}
    }}
    """.format(
        uuid=podcast.uuid,
        page=page,
        limitPerPage=limitPerPage,
    )
    response = requests.post(
        url=ENDPOINT,
        json={"query": query},
        headers=HEADERS
    )
    response_json = handle_response(response)
    episodes_json = response_json["data"]["getPodcastSeries"]["episodes"]
    episodes = []
    for episode_json in episodes_json:
        logger.debug(episode_json)
        episode = Episode(
            podcast=podcast,
            name=episode_json["name"],
            description=episode_json["description"],
            uuid=episode_json["uuid"],
            audioUrl=episode_json["audioUrl"],
        )
        episodes.append(episode)
    return episodes


def get_episode(uuid):
    """
    Retrieves an episode with the given UUID.

    Parameters:
        uuid (str): The UUID of the episode.

    Returns:
        Episode: The retrieved episode object.

    Raises:
        None.
    """
    if (episode := get_episode_if_exists(uuid)):
        return episode

    logger.debug(
        "Getting episode with uuid {uuid}".format(
            uuid=uuid,
        )
    )
    query = """
    query {{
        getPodcastEpisode(uuid:"{uuid}"){{
            uuid
            name
            description
            audioUrl
            podcastSeries{{
                uuid
                name
            }}
        }}
    }}
    """.format(
        uuid=uuid,
    )
    response = requests.post(
        url=ENDPOINT,
        json={"query": query},
        headers=HEADERS
    )
    response_json = handle_response(response)
    episode_json = response_json["data"]["getPodcastEpisode"]
    logger.debug(episode_json)
    episode = Episode(
        podcast=search_or_get_podcast(uuid=episode_json["podcastSeries"]["uuid"]),
        name=episode_json["name"],
        description=episode_json["description"],
        uuid=episode_json["uuid"],
        audioUrl=episode_json["audioUrl"],
    )
    return episode
