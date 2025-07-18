

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


    def print_authors(self):
        for a in self.author:
            print(a)

    def author_list(self):
        auth_list = []
        for a in self.author:
            auth_list.append(a.as_string())
        return auth_list

    def has_author(self):
        return isinstance(self.author, list) and len(self.author) > 0

    def encode(self):
        return self.__dict__

    def __str__(self):
        return f"Title: %s \n Author: %s{" " + "et al" if self.has_author and len(self.author) > 1 else ""}" % (self.title, self.author[0] if self.has_author() else "None")

    def __repr__(self):
        return "Reference: %s" % (self.title[0:25] + "..." if isinstance(self.title, str) and len(self.title) > 25 else self.title)


class Author:
    def __init__(self, given = None, family = None):
        self.given = given
        self.family = family

    def __eq__(self, other):
        if isinstance(other, Author):
            if other.family == self.family:
                return True
        return False

    def __str__(self):
        return "%s %s" % (self.given, self.family)

    def __repr__(self):
        return "Author Given: %s, Family: %s" % (self.given, self.family)

    def as_string(self):
        return self.family

    def encode(self):
        return self.__dict__


