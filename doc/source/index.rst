.. Simple Dictation App documentation master file, created by
   sphinx-quickstart on Wed Mar  4 16:43:51 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Simple Dictation App Documentation
==================================

Overview
--------

This is a very simple dictation app. It uses vosk [#fvosk]_ for speech recognition
and pyside6 [#fpyside]_ for the UI. Additionally the LanguageTool [#flt]_ is used
to correct the text output from the speech recognition.

Installation and Usage
^^^^^^^^^^^^^^^^^^^^^^

Clone the repository:

.. code-block:: sh
   :linenos:

    git clone https://github.com/wachjose88/simple-stt.git
    cd simple-stt

Install the requirements:

.. code-block:: sh
   :linenos:

    pip install -r requirements.txt
    cd dictation

This implementation does not include the models required for speech recognition.
You need to download the models you want to use from the vosk website [#fvoskmodels]_.
Unzip the downloaded models to a directory. Now run the app and provide the path to
the directory containing the models:

.. code-block:: sh
   :linenos:

    python3 main.py -md <PATH-TO-MODELS-DIRECTORY>

Build the Documentation
^^^^^^^^^^^^^^^^^^^^^^^

To build this documentation use the following commands:

.. code-block:: sh
   :linenos:

    cd doc
    make html
    make latexpdf


.. [#fvosk] https://alphacephei.com/vosk/ (last accessed March 25, 2026)
.. [#fpyside] https://www.qt.io/development/qt-framework/python-bindings
   (last accessed March 25, 2026)
.. [#flt] https://languagetool.org
   (last accessed March 25, 2026)
.. [#fvoskmodels] https://alphacephei.com/vosk/models
   (last accessed March 25, 2026)


Source Code Documentation
-------------------------

.. toctree::
   :maxdepth: 3

   main
   editor
   settings
   stt
   signals

