import sys
import os

sys.path.insert(0, os.path.abspath('../../'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'code_io.settings')
django.setup()

project = 'Code-io'
copyright = '2025, Команда 1, Группа s102'
author = 'Команда 1, Группа s102'
release = 'v1.0'

extensions = ['sphinx.ext.autodoc']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'inherited-members': False,
}

language = 'ru'

autodoc_inherit_docstrings = False
