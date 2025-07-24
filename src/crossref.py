from habanero import Crossref

import models as m


class CrossrefSearcher:
    def __init__(self, mailto, timeout):
        self.mailto = mailto
        self.timeout = timeout
        self.cr = Crossref(mailto = self.mailto, timeout = self.timeout)

    def search_title(self, title, authors):
        try:
            result = self.cr.works(query_title=title, query_author=authors)
            if result['status'] == 'ok':
                print("results found")
                if len(result['message']['items']) < 1:
                    print("no results found")
                    return None
                return result['message']['items'][0]
            else:
                print("error", result['status'])
                return None
        except Exception as e:
            print("major error")
            print(e)
            return None

    def search_doi(self, doi):
        try:
            result = self.cr.works(ids=doi)
            if result['status'] == 'ok':
                print("successful DOI")
                return result['message']
            else:
                print("error", result['status'])
                return None
        except Exception as e:
            print("major error")
            print(e)
            return None

    def search(self, ref):
        if ref.doi is not None:
            return self.search_doi(ref.doi)
        else:
            return self.search_title(ref.title, ref.author)

class CrossrefParser:

    def extract_author(self, authors):
        auth_list = []
        if authors is None:
            return
        for auth in authors:
            given = auth.get('given')
            family = auth.get('family')
            author = m.Author(given, family)
            auth_list.append(author)
        return auth_list

    def extract_date(self, res):
        try:
            date = res['published']['date-parts'][0][0]
        except(KeyError, IndexError, TypeError):
            date = None
        return date

    def extract_ref(self, res):
        ref = m.Reference(res.get('title', [None])[0],  # return list with None if no title to prevent out of range
                        self.extract_author(res.get('author')),
                        res.get('DOI'),
                        res.get('URL'),
                        self.extract_date(res),
                        res.get('container-title'),
                        res.get('volume'),
                        res.get('page'))
        return ref

    def extract_results(self, res):
        results = []
        for ref in res:
            if ref['score'] >= 50:
                results.append(self.extract_ref(ref))
        return results