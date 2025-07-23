import abc
from abc import abstractmethod

import utils
import parser
import crossref
import os

mailto = os.getenv("MAILTO")

class Evaluator(abc.ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def evaluation(self, src_ref, ext_ref):
        pass

    def evaluate(self, src_ref, ext_ref):
        return {
            "type": self.name(),
            "score": self.evaluation(src_ref, ext_ref)
        }

class BooleanEvaluator(Evaluator):
    def name(self):
        return "Boolean"


class BooleanTitleEvaluator(BooleanEvaluator):
    def evaluation(self, src_ref, ext_ref):
        if src_ref.title is None or ext_ref.title is None:
            return False
        return utils.normalise_str(src_ref.title) == utils.normalise_str(ext_ref.title)


class BooleanAuthorEvaluator(BooleanEvaluator):
    def evaluation(self, src_ref, ext_ref):
        if len(src_ref.author) == 0:
            return False
        for auth in src_ref.author:
            if auth not in ext_ref.author:
                return False
        return True


class BooleanDoiEvaluator(BooleanEvaluator):
    def evaluation(self, src_ref, ext_ref):
        if src_ref.doi is None:
            return "N/A"
        else:
            return src_ref.doi.lower() == ext_ref.doi.lower()



class BoolEvaluator:
    def match_title(self, src_ref, ext_ref):
        if src_ref.title is None or ext_ref.title is None:
            return False
        return utils.normalise_str(src_ref.title) == utils.normalise_str(ext_ref.title)

    def match_author(self, src_ref, ext_ref):
        if len(src_ref.author) == 0:
            return False
        for auth in src_ref.author:
            if auth not in ext_ref.author:
                return False
        return True

    def match_doi(self, src_ref, ext_ref):
        if src_ref.doi is None:
            return "N/A"
        else:
            return src_ref.doi.lower() == ext_ref.doi.lower()


    def evaluate(self, src_ref, ext_ref):
        return {
            'title': self.match_title(src_ref, ext_ref),
            'author': self.match_author(src_ref, ext_ref),
            'doi' : self.match_doi(src_ref, ext_ref)
        }

    def is_match(self, src_ref, ext_ref):
        return all(self.evaluate(src_ref, ext_ref).values())


class AdvanceEvaluator:
    def match_pages(self, src_ref, ext_ref):
        if src_ref.pages == None or ext_ref.pages == None:
            return "N/A"
        else:
            return src_ref.pages.strip() == ext_ref.pages.strip()


class EvaluationController:
    def __init__(self, stage1, stage2):
        self.stage1 = stage1
        self.stage2 = stage2
    def evaluate(self, src_ref, ext_ref):
        return {"stage": 1, "matches": self.stage1.is_match(src_ref, ext_ref), "results": self.stage1.evaluate(src_ref, ext_ref)}


def evaluate_bibliography(bibliography, file_name=""):
    evaluator = EvaluationController(BoolEvaluator(), None)
    parsed_bib = parser.XmlBibliography().parse(bibliography)
    results = []
    for ref in parsed_bib:
        search_results = crossref.CrossrefSearcher(mailto, 20).search(ref)
        if search_results is not None:
            found_ref = crossref.CrossrefParser().extract_ref(search_results)
            evaluation = evaluator.evaluate(ref, found_ref)
            results.append({'reference': ref, 'evaluation': evaluation, 'reference_located': found_ref})
        else:
            results.append({'reference': ref, 'evaluation': 'None', 'reference_located': 'Not Found'})

    print("finished, returning results")
    utils.export_json(results, file_name + (" - " if len(file_name) > 0 else "") + "verification results")
    return results
