# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

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

language = 'ru'

autodoc_inherit_docstrings = False
