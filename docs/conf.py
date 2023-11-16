# -*- coding: utf-8 -*-
import os, pkg_resources, datetime, time

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/stable/', None),
    'myst': ('https://myst-parser.readthedocs.io/en/latest', None),
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
    '_build',
    'example*',
]
pygments_style = 'sphinx'

# Options for HTML output
html_theme = 'furo'
html_title = 'Sybil'
htmlhelp_basename = project+'doc'

# Options for LaTeX output
latex_documents = [
  ('index',project+'.tex', project+u' Documentation',
   'Chris Withers', 'manual'),
]

autodoc_member_order = 'bysource'
nitpicky = True
nitpick_ignore = [
    ('py:class', 'Evaluator'),  # https://github.com/sphinx-doc/sphinx/issues/10785
    ('py:class', 'LexemeMapping'),  # https://github.com/sphinx-doc/sphinx/issues/10785
]
toc_object_entries = False
