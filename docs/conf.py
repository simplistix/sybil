# -*- coding: utf-8 -*-
import os, pkg_resources, datetime, time

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

intersphinx_mapping = {
    'https://docs.python.org/3/': None,
    'http://www.sphinx-doc.org/en/stable/': None,
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
    ]

# General
source_suffix = '.rst'
master_doc = 'index'
project = 'sybil'
build_date = datetime.datetime.utcfromtimestamp(int(os.environ.get('SOURCE_DATE_EPOCH', time.time())))
copyright = '2017 - %s Chris Withers' % build_date.year
version = release = pkg_resources.get_distribution(project).version
exclude_patterns = [
    'description.rst',
    '_build',
    'example*',
]
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'default' if on_rtd else 'classic'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

autodoc_member_order = 'bysource'
