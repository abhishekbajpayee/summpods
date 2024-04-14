from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    URLField,
    IntField,
    DateTimeField,
    ReferenceField,
)
from flask_admin.contrib.mongoengine import ModelView


class Podcast(Document):
    uuid = StringField(primary_key=True)
    name = StringField()
    description = StringField()
    itunesId = StringField()
    imageUrl = URLField()
    episodeCount = IntField()


class Episode(Document):
    uuid = StringField(primary_key=True)
    name = StringField()
    podcast = ReferenceField(Podcast)
    description = StringField()
    audioUrl = URLField()


class TranscriptionModel(Document):
    name = StringField(primary_key=True)


class SummarizationModel(Document):
    name = StringField(primary_key=True)


class Transcription(Document):
    """
    Model to represent a transcription. An assumption made here is that
    a transcription is uniquely defined by its episode (which uniquely
    belongs to a podcast), and transcription_model.
    """
    transcription_model = ReferenceField(TranscriptionModel)
    episode = ReferenceField(Episode)
    creation_date = DateTimeField(default=datetime.utcnow)
    text = StringField()


class Summary(Document):
    """
    Model to represent an episode summary. As assumption made here is that
    a summary is uniquely defined by its transcription, summarization_model,
    and prompt.
    """
    summarization_model = ReferenceField(SummarizationModel)
    transcription = ReferenceField(Transcription)
    prompt = StringField()
    creation_date = DateTimeField(default=datetime.utcnow)
    text = StringField()


# Admin views
class PodcastView(ModelView):
    column_list = (
        "uuid",
        "name",
        "description",
        "itunesId",
        "episodeCount",
    )


class EpisodeView(ModelView):
    column_list = (
        "uuid",
        "name",
        "podcast",
        "description",
        "audioUrl",
    )


class TranscriptionView(ModelView):
    column_list = (
        "transcription_model",
        "episode",
        "creation_date",
        "text",
    )

    
class SummaryView(ModelView):
    column_list = (
        "summarization_model",
        "transcription",
        "prompt",
        "creation_date",
        "text",
    )
