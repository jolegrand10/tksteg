# tksteg

A steganography application, written in Python, using TkInter.

Available for Windows and Linux.

Checked on Windows 10 and Ubuntu Focal Fossa 20.4.

To install necessary libs:

`$ pip install -r requirements.txt`

To build exe for Windows:

`$ python setup.py build `

To build exe for Linux, first:

`$ pip install pyinstaller`

and then, either use the spec file:

`$ pyinstaller tksteg.spec`

or execute the following 1-line command :

`$ pyinstaller main.py --hiddenimport PIL --hiddenimport PIL._imagingtk --hiddenimport PIL._tkinter_finder --name tksteg --onefile`

