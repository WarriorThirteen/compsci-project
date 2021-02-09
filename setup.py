from distutils.core import setup
import py2exe

setup(console=['main.py'])
# pyinstaller --noconfirm --onefile --windowed --add-data "C:/Users/arajj/OneDrive/Documents/School/Freemens/6th Form/0 Computing/0 Project/Documentation/2 Implementation/pygame_gui;pygame_gui/" --add-data "C:/Users/arajj/OneDrive/Documents/School/Freemens/6th Form/0 Computing/0 Project/Documentation/2 Implementation/resources;resources/"  ""