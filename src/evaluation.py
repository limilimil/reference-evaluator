import abc
from abc import abstractmethod

import utils
import parser
import crossref
import os

import rapidfuzz

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
        return "boolean"


class BooleanTitleEvaluator(BooleanEvaluator):
    def evaluation(self, src_title, ext_title):
        if src_title is None or ext_title is None:
            return 0.0
        return float(utils.normalise_str(src_title) == utils.normalise_str(ext_title))


class BooleanAuthorEvaluator(BooleanEvaluator):
    def evaluation(self, src_auth, ext_auth):
        if len(src_auth) == 0:
            return 0.0
        for auth in src_auth:
            if auth not in ext_auth:
                return 0.0
        return 1.0

class BooleanDoiEvaluator(BooleanEvaluator):
    def evaluation(self, src_doi, ext_doi):
        if src_doi is None:
            return "N/A"
        else:
            return float(src_doi.lower() == ext_doi.lower())

class BooleanDateEvaluator(BooleanEvaluator):
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        else:
            return float(src.strip() == ext.strip())

class BooleanPagesEvaluator(BooleanEvaluator):
    def evaluation(self, src_pages, ext_pages):
        if src_pages is None or ext_pages is None:
            return "N/A"
        else:
            return float(src_pages.strip() == ext_pages.strip())

class BooleanVolumeEvaluator(BooleanEvaluator):
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        else:
            return float(src.strip() == ext.strip())

class LevenshteinEvaluator(Evaluator):
    def name(self):
        return "levenshtein"

class LevenshteinTitleEvaluator(LevenshteinEvaluator):
    def evaluation(self, src, ext):
        return rapidfuzz.distance.Levenshtein.normalized_similarity(utils.normalise_str(src), utils.normalise_str(ext))

class LevenshteinDateEvaluator(LevenshteinEvaluator):
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        return rapidfuzz.distance.Levenshtein.normalized_similarity(src.strip(), ext.strip())

class LevenshteinVolumeEvaluator(LevenshteinEvaluator):
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        return rapidfuzz.distance.Levenshtein.normalized_similarity(src.strip(), ext.strip())


evaluator_registry = {
    "title": {
        "boolean": BooleanTitleEvaluator(),
        "levenshtein": LevenshteinTitleEvaluator()
    },
    "author": {
        "boolean": BooleanAuthorEvaluator()
    },
    "doi": {
        "boolean": BooleanDoiEvaluator()
    },
    "date": {
        "boolean": BooleanDateEvaluator(),
        "levenshtein": LevenshteinDateEvaluator()
    },
    "volume": {
        "boolean": BooleanVolumeEvaluator(),
        "levenshtein": LevenshteinVolumeEvaluator()
    },
    "pages": {
        "boolean": BooleanPagesEvaluator()
    }
}


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
            "evaluation-method": evaluations
        }

    #Placeholder function
    def aggregate(self, evaluations):
        return sum(evaluations)/len(evaluations)

    def evaluate(self, src_ref, ext_ref):
        results = {}
        for elem in self.config:
            results[elem] = self.evaluate_element(elem, src_ref, ext_ref)
        overall = all(results[elem]["score"] for elem in results)

        return {"overall": overall, "reference element": results}



def evaluate_bibliography(bibliography, config, file_name=""):
    evaluator = EvaluationController(config)
    parsed_bib = parser.XmlBibliography().parse(bibliography)
    results = []
    for ref in parsed_bib:
        search_results = crossref.CrossrefSearcher(mailto, 20).search(ref)
        if search_results is not None:
            found_ref = crossref.CrossrefParser().extract_ref(search_results)
            evaluation = evaluator.evaluate(ref, found_ref)
            results.append({'reference': ref, 'reference-located': found_ref, 'evaluation': evaluation})
        else:
            results.append({'reference': ref, 'reference-located': 'None Found', 'evaluation': 'None'})

    print("finished, returning results")
    utils.export_json(results, file_name + (" - " if len(file_name) > 0 else "") + "verification results")
    return results
