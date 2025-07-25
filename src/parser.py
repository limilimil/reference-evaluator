import re

from grobid_client.grobid_client import GrobidClient

import models as m

"""
Converts pdf file into parsable XML
Parameters:
input_path (str): File path of the pdf to be parsed
output_path (str): File path for the resulting xml file
config_path (str): Location of Grobid config file (optional)
"""
class PdfToXML:
    def __init__(self, input_path, output_path, config_path="./config.json"):
        self.input_path = input_path
        self.output_path = output_path
        self.config_path = config_path

    #Calls the grobid file to begin parsing
    def run(self):
        xml_path = self.input_path.with_suffix(".grobid.tei.xml")
        client = GrobidClient(config_path=self.config_path)
        client.process("processReferences", self.input_path.parent, self.output_path.parent, verbose=True)
        return (xml_path.is_file())


class XmlBibliography:
    # def __init__(self):

    def extract_text(self, ref, tag, attrib=None):
        result = ref.find(tag, attrib)
        return result.text if result is not None else None

    def parse_author(self, author):
        forename = self.extract_text(author, 'forename', {'type': 'first'})
        middle = self.extract_text(author, 'forename', {'type': 'middle'})
        if isinstance(forename, str) and isinstance(middle, str):
            forename = " ".join([forename, middle])
        surname = self.extract_text(author, 'surname')
        return m.Author(forename, surname)

    def parse_author_list(self, ref):
        authors = ref.find_all('author')
        auth_list = []
        for auth in authors:
            auth_list.append(self.parse_author(auth))
        return auth_list

    def extract_year(self, ref):
        result = ref.find('date')
        if result == None or not result.has_attr('when'):
            return
        date = result.get('when')
        date_regx = re.compile(r'^(?P<year>\d{4})')
        match = date_regx.match(date)
        return match.group('year') if match else None

    def extract_pages(self, ref):
        result = ref.find('biblScope', {'unit': 'page'})
        if result == None:
            return
        if result.has_attr('from') and result.has_attr('to'):
            pages = result['from'] + "-" + result['to']
            return pages
        else:
            return result.text

    def parse_ref(self, ref):
        title = self.extract_text(ref, 'title', {'type':'main'})
        authors = self.parse_author_list(ref)
        doi = self.extract_text(ref, 'idno', {'type': 'DOI'})
        date = self.extract_year(ref)
        volume = self.extract_text(ref, 'biblScope', {'unit': 'volume'})
        pages = self.extract_pages(ref)
        return m.Reference(title, authors, doi, date=date, volume=volume, pages=pages)

    def parse(self, soup):
        bib = soup.find_all('biblStruct')
        parsed_bib = []
        for ref in bib:
            parsed_bib.append(self.parse_ref(ref))
        return parsed_bib
