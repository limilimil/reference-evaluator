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
    def evaluation(self, src, ext):
        pass

    def evaluate(self, src, ext):
        return {
            "method": self.name(),
            "score": self.evaluation(src, ext)
        }

class BooleanEvaluator(Evaluator):
    def name(self):
        return "Boolean"


class BooleanTitleEvaluator(BooleanEvaluator):
    def evaluation(self, src_title, ext_title):
        if src_title is None or ext_title is None:
            return 0
        return int(utils.normalise_str(src_title) == utils.normalise_str(ext_title))


class BooleanAuthorEvaluator(BooleanEvaluator):
    def evaluation(self, src_auth, ext_auth):
        if len(src_auth) == 0:
            return 0
        for auth in src_auth:
            if auth not in ext_auth:
                return 0
        return 1


class BooleanDoiEvaluator(BooleanEvaluator):
    def evaluation(self, src_doi, ext_doi):
        if src_doi is None:
            return 0.5
        else:
            return int(src_doi.lower() == ext_doi.lower())


evaluator_registry = {
    "title": {
        "boolean": BooleanTitleEvaluator()
    },
    "author": {
        "boolean": BooleanAuthorEvaluator()
    },
    "doi": {
        "boolean": BooleanDoiEvaluator()
    }
}


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
    def __init__(self, config):
        self.config = config

    def evaluate_element(self, element, src_ref, ext_ref):
        src_elem = getattr(src_ref, element)
        ext_elem = getattr(ext_ref, element)
        eval_names = self.config[element]["evaluators"]
        evaluations = []

        for eval in eval_names:
            evaluator = evaluator_registry.get(element).get(eval)
            result = evaluator.evaluate(src_elem, ext_elem)
            evaluations.append(result)

        if len(eval_names) == 1:
            score = evaluations[0]["score"]
        else:
            score = self.aggregate(evaluations)

        return {
            "score": score,
            "evaluation": evaluations
        }

    #Placeholder function
    def aggregate(self, evaluations):
        return sum(evaluations)/len(evaluations)

    def evaluate(self, src_ref, ext_ref):
        results = {}
        for elem in self.config:
            results[elem] = self.evaluate_element(elem, src_ref, ext_ref)

        return {"results": results}



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
