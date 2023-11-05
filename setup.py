from setuptools import setup
import py2exe

setup(
    name='AbbeyAI',
    version='1.0',
    description='An AI application',
    author='Bryan Mina',
    console=['main.py'],
    packages=['data', 'plugins'],
    options={
        'py2exe': {
            'excludes': ['.vscode', '.gitignore', '.env']
        }
    }
)