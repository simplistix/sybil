from importlib import metadata

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'pytest': ('https://docs.pytest.org/en/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/stable/', None),
    'myst': ('https://myst-parser.readthedocs.io/en/latest', None),
}

# General
source_suffix = '.rst'
master_doc = 'index'
project = 'sybil'
copyright = '2017 onwards Chris Withers'
version = release = metadata.version(project)
exclude_patterns = [
    '_build',
    'example*',
]
pygments_style = 'sphinx'
autodoc_member_order = 'bysource'

# Options for HTML output
html_theme = 'furo'
htmlhelp_basename = project + 'doc'

nitpicky = True
nitpick_ignore = [
    ('py:class', 'Evaluator'),  # https://github.com/sphinx-doc/sphinx/issues/10785
    ('py:class', 'LexemeMapping'),  # https://github.com/sphinx-doc/sphinx/issues/10785
]
toc_object_entries = False
