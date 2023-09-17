import pymongo
from pymongo import MongoClient
import gridfs
from transformers import pipeline
from huggingsound import SpeechRecognitionModel


uri = "mongodb+srv://amrit:amrit123@cluster0.buro27m.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client['db']

fs = gridfs.GridFS(db)

reports = db['reports']


transcriber = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-english", device="cuda")

classifier = pipeline(model="facebook/bart-large-mnli", device_map="auto")

candidate_labels = ["elevator complaint", "hvac complaint", "plumbing complaint", "non-complaint"]

def infer(doc_id):
  recording = fs.get(doc_id)
  
  with open("recording.wav", "wb") as rec_file:
      # Write bytes to file
      rec_file.write(recording.read())
  
  audio_paths = ["recording.wav"]
  
  transcriptions = transcriber.transcribe(audio_paths)
  
  # print(transcriptions)
  
  scores = classifier(transcriptions[0]['transcription'], candidate_labels=candidate_labels)
  
  # print(scores)

  return {
      "text": scores['sequence'],
      "scores": dict(zip(scores['labels'], scores['scores']))
  }

cursor = db['fs.files'].watch()

for change in cursor:
  try:
    id = change['documentKey']['_id']
  
    result = infer(id)
    reports.insert_one(result | {'file_id': id})
  except KeyboardInterrupt:
    break

