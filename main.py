import sounddevice as sd
from pymongo import MongoClient
from scipy.io.wavfile import write
import wavio as wv
from gridfs import GridFS

if __name__ == '__main__':
    uri = "mongodb+srv://amrit:amrit123@cluster0.buro27m.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client['db']
    fs = GridFS(db)
    # reports = db['reports']

    # Sampling frequency
    freq = 16000

    # Recording duration
    duration = 10

    # Start recorder with the given values of
    # duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()
    print("done recording")

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("recording0.wav", freq, recording)
    print("recording 0 saved")

    # Convert the NumPy array to audio file
    wv.write("recording1.wav", recording, freq, sampwidth=2)

    print("recording 1 saved")

    # upload the file to mongodb
    with open("recording1.wav", "rb") as f:
        encoded = f.read()
    print("file read")

    fs.put(encoded, filename="recording1.wav")
    print("file uploaded")

    client.close()
    print("connection closed")