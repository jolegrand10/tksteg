from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might need
# fine tuning.


build_options = {'packages': [],
                 'excludes': []}


if sys.platform=='win32':
    base = 'Win32GUI'

    executables = [
        Executable('main.py', base=base, target_name = 'tksteg', icon="tksteg.ico", shortcutDir="DesktopFolder",
                   shortcutName="TkSteg",)
    ]

    setup(name='tksteg',
          version = '1.0',
          description = 'Simple steganography',
          options = {'build_exe': build_options},
          executables = executables)
elif sys.platform=='linux':
    print("""To build a single file exe @ linux, use rather:
   $ pyinstaller tksteg.spec
or single line command:
   $ pyinstaller main.py --hiddenimport PIL --hiddenimport PIL._imagingtk
     --hiddenimport PIL._tkinter_finder --name tksteg""")
else:
    print("Only win and linux supported at the moment")
