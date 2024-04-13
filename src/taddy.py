import requests
import logging
from src.utils import KEYS
from src.models import (
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


def search_podcast(term):
    """
    Retrieves podcast series information by searching for a given term.

    Args:
        term (str): The search term used to find the podcast series.

    Returns:
        dict or bool: If the search is successful, it returns a dictionary
                      containing the podcast series information. If the
                      search is unsuccessful, it returns False.

    Raises:
        None
    """
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
