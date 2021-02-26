# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import re
from os.path import join, dirname

# -- Project information -----------------------------------------------------

project = 'guniflask'
copyright = '2018-2021, jadbin'
author = 'jadbin'


# The short X.Y version
def read_version():
    p = join(dirname(dirname(__file__)), 'guniflask', '__init__.py')
    with open(p, 'r', encoding='utf-8') as f:
        return re.search(r"__version__ = '([^']+)'", f.read()).group(1)


version = read_version()
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_theme_options = {
    'description': 'flask + gunicorn, scaffolding tool for web services',
    'github_user': 'jadbin',
    'github_repo': 'guniflask',
    'github_button': False,
    'travis_button': True,
    'font_family': '"Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif',
    'font_size': '14px',
    'code_font_size': '12px',
    'note_bg': '#E5ECD1',
    'note_border': '#BFCF8C',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_sidebars = {
    '**': [
        'about.html', 'navigation.html', 'searchbox.html',
    ]
}
