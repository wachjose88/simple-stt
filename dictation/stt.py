# MIT License
#
# Copyright (c) 2026 Josef Wachtler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The stt module provides the speech recognition.

This module provides a thread for speech recognition. It listens to the
microphone and places the recorded chunks in a queue. The thread then reads
from the queue and tries to recognize the spoken words.
"""

import json
import logging
import queue

from PySide6.QtCore import QThread
import sounddevice as sd
from vosk import Model, KaldiRecognizer

logger = logging.getLogger('dictation.stt')
"""Logger instance for the speech recognition."""

record_queue = queue.Queue()
"""Instance of the queue to save the recorded chunks."""

def record_callback(indata, frames, time, status):
    """The callback function for saving the recorded chunks.

    This callback function receives the recorded chunks and saves them
    to the queue.

    Arguments:
        indata: The recorded chunks.
        frames: The number of frames saved.
        time: The time of calling.
        status: The status of the call.
    """
    if status:
        logger.debug(f'STT Record callback status: {status}')
    record_queue.put(bytes(indata))


class SpeechToText(QThread):
    """The main thread for speech recognition.

    This class represents the main thread for speech recognition.
    It initializes the microphone, loads the model and performs
    the speech recognition on the recorded chunks.
    The recognized text is sent to the UI with a signal.

    Attributes:
        signals (QObject): a connection to the signals.
        stop (bool): False if the thread should be stopped.
        model_name (str): the name of the model.
        model (Model): the initialized model.
        recognizer (KaldiRecognizer): the speech recognizer.
        samplerate (int): the sampling rate of the microphone.

    Arguments:
        signals (QObject): a connection to the signals.
    """

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
        """The main loop of the thread for speech recognition."""
        self.model = Model(str(self.model_name))
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.recognizer.SetWords(False)
        try:
            with sd.RawInputStream(dtype='int16',
                                   channels=1,
                                   callback=record_callback):
                while not self.stop:
                    self.signals.model_ready.emit()
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


class CorrectText(QThread):
    """The thread for correcting the text.

    This class represents a thread to correct the text using
    the language tool.

    Attributes:
        signals (QObject): a connection to the signals.
        tool (LanguageTool): Language Tool object.
        text (str): the text to correct.

    Arguments:
        signals (QObject): a connection to the signals.
        tool (LanguageTool): Language Tool object.
    """

    def __init__(self, signals, tool):
        super().__init__()
        self.signals = signals
        self.tool = tool
        self.text = ''

    def run(self):
        """The main loop of the thread for correcting the text."""
        text = self.tool.correct(self.text)
        self.signals.correction_finished.emit(text)
