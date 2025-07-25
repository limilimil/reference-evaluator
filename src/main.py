'''
Example project usage
'''


from pathlib import Path

from bs4 import BeautifulSoup

from parser import PdfToXML

import os
import evaluation
import json

mailto = os.getenv("MAILTO")

path = Path.cwd().joinpath("resources", "test-data", "compressed.tracemonkey-pldi-09.pdf")

result_path = path.with_suffix(".grobid.tei.xml")
grobid_config = Path.cwd().joinpath("grobid-config.json")
config_path = Path.cwd().joinpath("example-config.json")

example_config = {
    "title": {
        "evaluators": {
            "boolean": 1.0,
            "levenshtein": 3.0
        }
    },
    "author": {
        "evaluators": {
            "boolean": 1.0
        }
    },
    "doi": {
        "evaluators": {
            "boolean": 1.0
        }
    },
    "date": {
        "evaluators": {
            "boolean": 1.0,
            "levenshtein": 1.0
        }
    },
    "volume": {
        "evaluators": {
            "levenshtein": 1.0
        }
    },
    "pages": {
        "evaluators": {
            "boolean": 1.0
        }
    }
}

with open(config_path) as c:
    config = json.load(c)

pdftoXML = PdfToXML(path, path, grobid_config)
parsed = pdftoXML.run()

if parsed:
    with open(result_path) as my_file:
        soup = BeautifulSoup(my_file, "lxml-xml")
        results = evaluation.evaluate_bibliography(soup, config, mailto, "compressed.tracemonkey-pldi-09")

