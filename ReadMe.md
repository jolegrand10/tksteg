# tksteg

A simple steganography application, written in Python, using TkInter.

Available for Windows and Linux.

Checked on Windows 10 and Ubuntu Focal Fossa 20.4.

## Usage

Double-click the icon (Windows, Linux) or execute from the command line (Linux) to display the Graphical User Interface.

"Encode" means "merge the text in the image".

Conversely, "Decode" is for extracting a text from an image.

Tksteg builds a log file ("tksteg.log").

## Installation from sources

To install necessary libs:

`$ pip install -r requirements.txt`

To build exe for Windows:

`$ python setup.py build `

To build installation file (msi file) for Windows 

`$ python setup.py bdist_msi`

To build exe for Linux, first:

`$ pip install pyinstaller`

and then, either use the spec file:

`$ pyinstaller tksteg.spec`

or execute the following 1-line command :

`$ pyinstaller main.py --hiddenimport PIL --hiddenimport PIL._imagingtk --hiddenimport PIL._tkinter_finder --name tksteg --onefile`

## Known limitations

Image files having non-ASCII chars in their path or name cannot be loaded because CV2 fails to open them. A workaround is to move and/or rename such files to avoid non-ASCII chars.

Text files exceeding image capacity are truncated.

Alerts are issued and warnings are logged when this happens.

Encoded images cannot be saved in JPG because its compression scheme looses the information on low-weight bits.
Suitable image formats are proposed, like PNG.
