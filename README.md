# Simple Dictation App (STT)

This is a very simple dictation app. It uses 
[vosk](https://alphacephei.com/vosk/)
for speech recognition and 
[pyside6](https://www.qt.io/development/qt-framework/python-bindings)
for the UI. Additionally the
[LanguageTool](https://languagetool.org)
is used to correct the text output from the speech
recognition.

## Installation and Usage

Clone the repository:

```sh
git clone https://github.com/wachjose88/simple-stt.git
cd simple-stt
```

Install the requirements:

```sh
pip install -r requirements.txt
cd dictation
```

This implementation does not include the models required for speech
recognition. You need to download the models you want to use from the
[vosk website](https://alphacephei.com/vosk/models). Unzip the 
downloaded models to a directory. Now run
the app and provide the path to the directory containing the models:

```sh
python3 main.py -md <PATH-TO-MODELS-DIRECTORY>
```

## Build the Documentation

To build the documentation use the following commands:

```sh
cd doc
make html
make latexpdf
```