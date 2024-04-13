from datetime import datetime
from flask_mongoengine import MongoEngine

# initalize MongoEngine
db = MongoEngine()


class Podcast(db.Document):
    uuid = db.StringField(primary_key=True)
    name = db.StringField()
    description = db.StringField()
    itunesId = db.StringField()
    imageUrl = db.URLField()
    episodeCount = db.IntField()


class Episode(db.Document):
    uuid = db.StringField(primary_key=True)
    name = db.StringField()
    podcast = db.ReferenceField(Podcast)
    description = db.StringField()
    audioUrl = db.URLField()


class TranscriptionModel(db.Document):
    name = db.StringField(primary_key=True)


class SummarizationModel(db.Document):
    name = db.StringField(primary_key=True)


class Transcription(db.Document):
    """
    Model to represent a transcription. An assumption made here is that
    a transcription is uniquely defined by its episode (which uniquely
    belongs to a podcast), and transcription_model.
    """
    transcription_model = db.ReferenceField(TranscriptionModel)
    # podcast = db.ReferenceField(Podcast)
    episode = db.ReferenceField(Episode)
    creation_date = db.DateTimeField(default=datetime.utcnow)
    text = db.StringField()


class Summary(db.Document):
    """
    Model to represent an episode summary. As assumption made here is that
    a summary is uniquely defined by its transcription, summarization_model,
    and prompt.
    """
    summarization_model = db.ReferenceField(SummarizationModel)
    transcription = db.ReferenceField(Transcription)
    prompt = db.StringField()
    creation_date = db.DateTimeField(default=datetime.utcnow)
    text = db.StringField()
