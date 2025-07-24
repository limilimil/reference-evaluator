import json
from pathlib import Path

from bs4 import BeautifulSoup

from parser import PdfToXML
import evaluation
import models
import utils

path = Path.cwd().joinpath("resources", "test-data", "compressed.tracemonkey-pldi-09.pdf")

result_path = path.with_suffix(".grobid.tei.xml")
grobid_config = Path.cwd().joinpath("config.json")
config_path = Path.cwd().joinpath("example-config.json")

example_config = {
    "title": {
        "evaluators": ["boolean"]
    },
    "author": {
        "evaluators": ["boolean"]
    },
    "doi": {
        "evaluators": ["boolean"]
    },
    "pages": {
        "evaluators": ["boolean"]
    }

}

with open(config_path) as c:
    config = json.load(c)

pdftoXML = PdfToXML(path, path, grobid_config)
parsed = pdftoXML.run()

if parsed:
    with open(result_path) as my_file:
        soup = BeautifulSoup(my_file, "lxml-xml")
        results = evaluation.evaluate_bibliography(soup, config, "compressed.tracemonkey-pldi-09")
