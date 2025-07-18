from pathlib import Path

from bs4 import BeautifulSoup

from parser import PdfToXML
import evaluation

path = Path.cwd().joinpath("resources", "test-data", "compressed.tracemonkey-pldi-09.pdf")

result_path = path.with_suffix(".grobid.tei.xml")
config_path = Path.cwd().joinpath("config.json")

pdftoXML = PdfToXML(path, path, config_path)
parsed = pdftoXML.run()

if parsed:
    with open(result_path) as my_file:
        soup = BeautifulSoup(my_file, "lxml-xml")
        results = evaluation.evaluate_bibliography(soup, "compressed.tracemonkey-pldi-09")
