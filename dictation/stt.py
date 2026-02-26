import json
import logging
import queue
from time import sleep

from PySide6.QtCore import QThread
import sounddevice as sd
from vosk import Model, KaldiRecognizer

logger = logging.getLogger('dictation.stt')

record_queue = queue.Queue()

def record_callback(indata, frames, time, status):
    if status:
        logger.debug(f'STT Record callback status: {status}')
    record_queue.put(bytes(indata))


class SpeechToText(QThread):

    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.stop = False
        self.model_name = None
        self.model = None
        self.recognizer = None
        logger.debug(sd.query_devices())
        device_info = sd.query_devices(sd.default.device[0], 'input')
        self.samplerate = int(device_info['default_samplerate'])
        logger.debug(device_info)

    def run(self):
        self.model = Model(str(self.model_name))
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.recognizer.SetWords(False)
        try:
            with sd.RawInputStream(dtype='int16',
                                   channels=1,
                                   callback=record_callback):
                while not self.stop:
                    data = record_queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        recognizer_result = self.recognizer.Result()
                        # convert the recognizer_result string into a dictionary
                        result_dict = json.loads(recognizer_result)
                        text = result_dict.get('text', '')
                        if text != '':
                            logger.debug(recognizer_result)
                            self.signals.set_text_to_view.emit(text)
                        else:
                            logger.debug('no input sound')

        except Exception as e:
            logger.error(str(e))
