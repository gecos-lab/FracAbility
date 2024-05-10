# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
from datetime import date
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))

# The master toctree document.
master_doc = "index"

# -- Project information -----------------------------------------------------

project = 'FracAbility'
copyright = "2023-{},  Gabriele Benedetti".format(date.today().year)
author = 'Gabriele Benedetti'

# The full version, including alpha/beta/rc tags
import fracability as fracability

version = fracability.__version__
release = version

# -- General configuration ---------------------------------------------------

html_logo = "images/logo_small.png"

html_context = {
   # ...
   "default_mode": "light"
}

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "nbsphinx"
]
napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True
napoleon_use_rtype = False
nbsphinx_execute = 'never'
# # Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

master_doc = "index"
html_theme = 'sphinx_book_theme'


# # Add any paths that contain custom static files (such as style sheets) here,
# # relative to this directory. They are copied after the builtin static files,
# # so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/gbene/FracAbility",
    "repository_branch": "master",
    "use_edit_page_button": True,
    "use_source_button": True,
    "use_issues_button": True,
    # "use_repository_button": True,
    "use_download_button": True,
    "use_sidenotes": True,
    "show_toc_level": 2,
    # "announcement": (
    #     "⚠️The latest release refactored our HTML, "
    #     "so double-check your custom CSS rules!⚠️"
    # ),
    "logo": {
        "image_dark": "_static/logo-wide-dark.svg",
        # "text": html_title,  # Uncomment to try text with logo
    },
    "icon_links": [
        {
            "name": "Package latest release",
            "url": "https://pypi.org/project/FracAbility/",
            "icon": "https://img.shields.io/github/release/gbene/FracAbility?&sort=semver&color=orange",
            "type": "url",
        },
        {
            "name": "Star on GitHub!",
            "url": "https://github.com/gbene/FracAbility",
            "icon": "https://img.shields.io/github/stars/gbene/fracability.svg?style=social&label=Stars",
            "type": "url",
        },
        {
            "name": "Report issues!",
            "url": "https://github.com/gbene/FracAbility/issues",
            "icon": "fa-solid fa-triangle-exclamation",
        }
    ],
    # For testing
    # "use_fullscreen_button": False,
    # "home_page_in_toc": True,
    # "extra_footer": "<a href='https://google.com'>Test</a>",  # DEPRECATED KEY
    # "show_navbar_depth": 2,
    # Testing layout areas
    # "navbar_start": ["test.html"],
    # "navbar_center": ["test.html"],
    # "navbar_end": ["test.html"],
    # "navbar_persistent": ["test.html"],
    # "footer_start": ["test.html"],
    # "footer_end": ["test.html"]
}