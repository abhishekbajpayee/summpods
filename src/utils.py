from rq import Queue
from redis import Redis
import yaml

# load yaml file with API keys
KEYS = None
with open("/.secrets", "r") as f:
    KEYS = yaml.safe_load(f)

if KEYS is None:
    raise Exception("Could not load secrets file!")

# create RQ queue
queue = Queue(connection=Redis())
