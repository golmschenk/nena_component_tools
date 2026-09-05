import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path("../../src/nena_component_tools").absolute()))

project = "nena_component_tools"
project_copyright = f'2026 - {datetime.datetime.now().year}, Greg Olmschenk'
author = "Greg Olmschenk"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []
source_suffix = [".rst", ".md"]
autodoc_class_signature = 'separated'
autodoc_default_options = {
    'special-members': None,
}

html_theme = "furo"
html_static_path = ["_static"]
