import sys
from cx_Freeze import setup, Executable

setup(
    name = "Hearing Test",
    version = "0.1",
    description = "Hearing testing tool.",
    author = "Mikhail Karasikov",
    executables = [Executable("HearingTest.py", base = "Win32GUI", icon="icon.ico")]
)
