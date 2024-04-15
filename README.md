# summpods
Use LLMs to generate podcast summaries.

## Project outline
I use the following to put everything together:
- [Taddy API](https://taddy.org/developers/podcast-api) to search podcasts, get episodes and fetch audio files
- Use OpenAI whisper API to transcribe audio files; split files in chunks to get around file size limit
- Use OpenAI completion API to summarize transcriptions
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) for web app
- MongoDB [MongoEngine](https://docs.mongoengine.org/) for persistent data model storage
- [Material](https://m3.material.io/components) for page UI rendering
- [pydub](https://pypi.org/project/pydub/) library for audio file chunking
- [Bazel](https://bazel.build/) for builds

### Few dev notes
- I tried to use Bard and GPT-4 to research which libraries to use / how / why. GPT-4 was very helpful. For
code completion, I used [Codeium](https://codeium.com/) in VSCode for code completion which I also found very
useful. Using these tools, I was able to put this together in roughly 50-60 hrs of total coding time which I
had not expected :-)
- I was only able to use gpt-3.5-turbo model because OpenAI doesn't provide access to gpt-4 until you pay $1 in
API use billing. Using gpt-4 would have been nice because of the larger context window and I wouldn't have had
to write some code to split transcriptions into chunks. Even after transcribing and summarizing 20-30 hrs of
podcast content during testing, I wasn't able to accumulate $1 in billings. This goes to show how cheap this
stuff already is and it will only get cheaper from here.

## Setup
Create a text file called 'keys' with API keys in:
```
~/.secrets/keys
```
with contents:
```
OPENAI_KEY: "<OPENAI_KEY>"
TADDY_USER_ID: "<TADDY_USER_ID>"
TADDY_KEY: "TADDY_API_KEY"
```

## Run web app
Build is containerized and portable. To run web app, clone repo, ensure docker is installed and port 80 on
host is accessible. Then run following in repo root:
```
./bzl run //src:wsgi
```
and visit the public IP address for the host.

## Usage
Search for podcast...
![home](https://github.com/abhishekbajpayee/summpods/blob/main/src/images/home.png?raw=true)

View episodes...
![home](https://github.com/abhishekbajpayee/summpods/blob/main/src/images/podcast.png?raw=true)

Select episode to summarize...
![home](https://github.com/abhishekbajpayee/summpods/blob/main/src/images/episodes.png?raw=true)

Wait for summarization to finish (can take few minutes depending on episode length)...
![home](https://github.com/abhishekbajpayee/summpods/blob/main/src/images/wait.png?raw=true)

View summary on "Summaries" page...
![home](https://github.com/abhishekbajpayee/summpods/blob/main/src/images/summary.png?raw=true)
