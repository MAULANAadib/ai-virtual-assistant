from datetime import datetime
import math
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import keyboard
import os
from dotenv import load_dotenv

load_dotenv()


import google.cloud.texttospeech as tts
import pygame
import time


from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    try: 
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        print('')

# PARAMETERS #
activationWords = ['computer', 'nana', 'alex',]
tts_type = 'local' 


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = male, 1 = female


def google_text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])

    text_input = tts.SynthesisInput(text=text)

    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )

    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    return response.audio_content


chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))


appId = '5R49J7-J888YX9J2V'
wolframClient = wolframalpha.Client(appId)

def speak(text, rate = 120):
    time.sleep(0.3)
    try:     
        if tts_type == 'local':
            engine.setProperty('rate', rate) 
            engine.say(text, 'txt')
            engine.runAndWait()
        if tts_type == 'google':
            speech = google_text_to_wav('en-US-News-K', text)
            pygame.mixer.init(frequency=12000, buffer = 512)
            speech_sound = pygame.mixer.Sound(speech)
            speech_length = int(math.ceil(pygame.mixer.Sound.get_length(speech_sound)))
            speech_sound.play()
            time.sleep(speech_length)
            pygame.mixer.quit()
 
    except KeyboardInterrupt:
        try:
            if tts_type == 'google':
                pygame.mixer.quit()
        except:
            pass
        return


def parseCommand():
    with noalsaerr():
        listener = sr.Recognizer()
        print('Listening for a command')

        with sr.Microphone() as source:
            listener.pause_threshold = 2
            input_speech = listener.listen(source)

        try:
            print('Recognizing speech...')
            query = listener.recognize_google(input_speech, language='en_gb')
            print(f'The input speech was: {query}')

        except Exception as exception:
            print('I did not quite catch that')
            print(exception)

            return 'None'

        return query

def search_wikipedia(keyword=''):
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        return 'No result received'
    try: 
        wikiPage = wikipedia.page(searchResults[0]) 
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframalpha(keyword=''):
    response = wolframClient.query(keyword)
  

    if response['@success'] == 'false':
        speak('I could not compute')
    else: 
        result = ''
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            result = listOrDict(pod1['subpod'])
            return result.split('(')[0]
        else:
            question = listOrDict(pod0['subpod'])
            question = question.split('(')[0]
            return question


# Main loop
if __name__ == '__main__': 
    speak('The systems starting.', 120)

    while True:
        query = parseCommand().lower().split()

        if query[0] in activationWords and len(query) > 1:
            query.pop(0)

            # Set commands
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Hello, broo!')
                else:
                    query.pop(0) 
                    speech = ' '.join(query) 
                    speak(speech)


            if query[0] == 'open' and query[1] == 'chrome':
                speak('Opening... ')
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)


            if query[0] == 'in' and query[1] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Searching in wikipedia')
                time.sleep(2)
                speak(search_wikipedia(query))
                print(search_wikipedia(query))


            if query[0] == 'compute' or query[0] == 'computer':
                query = ' '.join(query[1:])
                try:
                    result = search_wolframalpha(query)
                    speak(result)
                    print(result)
                except:
                    speak('Unable to compute')
                    

            if query[0] == 'note':
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(now)
                    newFile.write(' ')
                    newFile.write(newNote)
                speak('Note written')

            if query[0] == 'exit':
                speak('Goodbye, bro')
                break
