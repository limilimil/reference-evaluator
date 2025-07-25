import re

from grobid_client.grobid_client import GrobidClient

import models as m

"""
Converts pdf file into parsable XML
Attributes:
    input_path (str): File path of the pdf to be parsed
    output_path (str): File path for the resulting XML file
    config_path (str): Location of Grobid config file
Methods:
    run:
        Calls the Grobid client to parse PDF
"""
class PdfToXML:
    def __init__(self, input_path, output_path, config_path="./config.json"):
        self.input_path = input_path
        self.output_path = output_path
        self.config_path = config_path

    """
    Calls the Grobid client begin parsing

    Parameters: None
    Returns:
        bool: True if parsing was successful
    """
    def run(self):
        xml_path = self.input_path.with_suffix(".grobid.tei.xml") # File path of resulting xml
        client = GrobidClient(config_path=self.config_path)
        client.process("processReferences", self.input_path.parent, self.output_path.parent, verbose=True) #Grobid configurations
        return (xml_path.is_file()) #Checks if XML file exists


"""
Converts Grobid XML file to data objects
Attributes: None
Methods:
    extract_text (ref, tag, attrib):
        Finds a specified XML tag and returns its text content
    parse_author (author):
        Transforms an individual author tag to an Author instance
    parse_author_list (ref):
        Extracts all authors of a reference
    extract_year (ref):
        Parses publishing year as a string
    extract_pages (ref):
        Parses pages element as a string
    parse_ref (ref):
        Transforms an individual reference into a Reference object
    parse (soup):
        Parses entire bibliography and returns a list of Reference instances
"""
class XmlBibliography:
    """
    Finds a specified XML tag and returns its text content
    Parameters:
        ref (BeautifulSoup): XML parser Soup object
        tag (str): The XML tag to find
        attrib (str): XML tag attrib to find (Optional)
    Returns:
        str: Inner text content of the tag found
    """
    def extract_text(self, ref, tag, attrib=None):
        result = ref.find(tag, attrib)
        return result.text if result is not None else None

    """
    Transforms an individual author tag to an Author instance
    Parameters:
        author (BeautifulSoup): XML Soup object author tag 
    Returns:
        Author: Name elements parsed into an Author instance
    """
    def parse_author(self, author):
        forename = self.extract_text(author, 'forename', {'type': 'first'})
        middle = self.extract_text(author, 'forename', {'type': 'middle'})
        if isinstance(forename, str) and isinstance(middle, str):
            forename = " ".join([forename, middle]) # Combine forename and middle name
        surname = self.extract_text(author, 'surname')
        return m.Author(forename, surname)

    """
    Extracts all authors of a reference
    Parameters:
        ref (BeautifulSoup): XML reference Soup object
    Returns:
        list[Author]: Collection of parsed Author objects
    """
    def parse_author_list(self, ref):
        authors = ref.find_all('author')
        auth_list = []
        for auth in authors:
            auth_list.append(self.parse_author(auth))
        return auth_list

    """
    Parses publishing year as a string
    Parameters:
        ref (BeautifulSoup): XML reference Soup object
    Returns:
        str: year
    """
    def extract_year(self, ref):
        result = ref.find('date')
        if result is None or not result.has_attr('when'): # return if no when attribute
            return None
        date = result.get('when')
        date_regx = re.compile(r'^(?P<year>\d{4})') # regex for parsing year into capture group 'year'
        match = date_regx.match(date)
        return match.group('year') if match else None

    """
    Parses pages element as a string
    Parameters:
        ref (BeautifulSoup): XML reference Soup object
    Returns:
        str: pages
    """
    def extract_pages(self, ref):
        result = ref.find('biblScope', {'unit': 'page'})
        if result == None:
            return
        if result.has_attr('from') and result.has_attr('to'):
            pages = result['from'] + "-" + result['to']
            return pages
        else:
            return result.text
    """
    Transforms an individual reference into a Reference object
    Parameters:
        ref (BeautifulSoup): Single reference XML Parser Soup object 
    Returns:
        Reference: a instance object with parsed elements 
    """
    def parse_ref(self, ref):
        title = self.extract_text(ref, 'title', {'type':'main'})
        authors = self.parse_author_list(ref)
        doi = self.extract_text(ref, 'idno', {'type': 'DOI'})
        date = self.extract_year(ref)
        volume = self.extract_text(ref, 'biblScope', {'unit': 'volume'})
        pages = self.extract_pages(ref)
        return m.Reference(title, authors, doi, date=date, volume=volume, pages=pages)

    """
    Parses entire bibliography and returns a list of Reference instances
    Parameters:
        soup (BeautifulSoup): XML Parser Soup object of entire bibliography 
    Returns:
        list[Reference]: all parsed references
    """
    def parse(self, soup):
        bib = soup.find_all('biblStruct') # Name of a reference element tag on Grobid XML files
        parsed_bib = []
        for ref in bib:
            parsed_bib.append(self.parse_ref(ref))
        return parsed_bib
