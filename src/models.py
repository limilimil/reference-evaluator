"""
Data Models
"""

"""
Object for storing reference data

Attributes:
    title(str):
        Title of the reference
    author(list[Author]):
        The authors specified in reference stored as a list of Author objects
    doi(str):
        DOI number, if provided in a reference
    url(str):
        hyperlink if provided in a reference
    date(str):
        Year the referenced material was published
    journal(str):
        Title of the publishing journal
    volume(str):
        A numerical value as a string of the volume element
    pages(str):
        A numerical value as a string of the pages element 

Methods:
    print_authors:
        Prints out each author on a seperate line
    author_list:
        Converts authors into strings and returns as a list
    has_author:
        Checks if author list is empty
    encode:
        Converts Reference object to dict for JSON export
"""
class Reference:
    def __init__(self, title=None, author=None, doi=None, url=None, date=None, journal=None, volume=None, pages=None):
        self.title = title
        self.author = author
        self.doi = doi
        self.url = url
        self.date = date
        self.journal = journal
        self.volume = volume
        self.pages = pages

    """
    Prints out each author on a seperate line

    Parameters: None
    Returns: None
    """
    def print_authors(self):
        for a in self.author:
            print(a)

    """
    Converts authors into strings and returns as a list

     Parameters: None

     Returns:
         list[str]: list of author names
     """
    def author_list(self):
        auth_list = []
        for a in self.author:
            auth_list.append(a.as_string())
        return auth_list

    """
    Checks if author list is empty

     Parameters: None

     Returns:
         bool: False if empty
     """
    def has_author(self):
        return isinstance(self.author, list) and len(self.author) > 0

    """
    Converts Reference object to dict for JSON export

     Parameters: None

     Returns:
         dict: Attributes converted into key-value pairs
     """
    def encode(self):
        return self.__dict__

    def __str__(self):
        return f"Title: %s \n Author: %s{" " + "et al" if self.has_author and len(self.author) > 1 else ""}" % (self.title, self.author[0] if self.has_author() else "None")

    def __repr__(self):
        return "Reference: %s" % (self.title[0:25] + "..." if isinstance(self.title, str) and len(self.title) > 25 else self.title)

"""
For storing author data

Attributes:
    given(str):
        First name of an author
    family(str):
        Last name of an author

Methods:
    as_string:
        Returns a string of the author's name
    encode:
        Converts Author object to dict for JSON export
"""
class Author:
    def __init__(self, given = None, family = None):
        self.given = given
        self.family = family

    def __eq__(self, other):
        if isinstance(other, Author):
            if other.family == self.family: # Checks only if last names match
                return True
        return False

    def __str__(self):
        return "%s %s" % (self.given, self.family)

    def __repr__(self):
        return "Author Given: %s, Family: %s" % (self.given, self.family)

    """
    Returns a string of the author's name

     Parameters: None

     Returns:
         str: String of the author's name
     """
    def as_string(self):
        return self.family

    """
    Converts Author object to dict for JSON export

     Parameters: None

     Returns:
         dict: Attributes converted into key-value pairs
     """
    def encode(self):
        return self.__dict__


