"""
For comparing references and analysing the validity of their components
"""

import abc
from abc import abstractmethod
from statistics import fmean

import utils
import parser
import crossref

import rapidfuzz

"""
Abstract class for evaluator sub classes
Attributes: None
Methods:
    name:
        Returns the name of the evaluator
    evaluation (src, ext):
        Abstract method for comparing source reference component against externally located reference component
    evaluate (src, ext):
        Calls the evaluation method and returns a formatted response
"""
class Evaluator(abc.ABC):
    """
    Returns the name of the evaluator
    Parameters: None
    Returns:
        str: Name of the evaluation method (class name)
    """
    @abstractmethod
    def name(self):
        pass

    """
    Abstract method for comparing reference components
    Parameters: 
        src: The original reference
        ext: Reference sourced externally
    """
    @abstractmethod
    def evaluation(self, src, ext):
        pass
    """
    Calls the evaluation method and returns a formatted response
    Parameters: 
        src: The original reference
        ext: Reference sourced externally
    Returns:
        dict: evaluator's name and the evaluation score
    """
    def evaluate(self, src, ext):
        return {
            "method": self.name(),
            "score": self.evaluation(src, ext)
        }

"""
Abstract class for boolean evaluators
Methods:
    name:
        Returns the name of the evaluator
"""
class BooleanEvaluator(Evaluator):
    """
    Returns the name of the evaluator
    Parameters: None
    Returns:
        str: Name of the evaluation method (class name)
    """
    def name(self):
        return "boolean"

"""
Reference title component evaluation with boolean algorithm
Methods:
    evaluation (src_title, ext_title):
        the evaluation algorithm
"""
class BooleanTitleEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src_title (str): Source Reference title attribute
        ext_title (str): External Reference title attribute
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src_title, ext_title):
        if src_title is None or ext_title is None:
            return 0.0
        return float(utils.normalise_str(src_title) == utils.normalise_str(ext_title))

"""
Reference author component evaluation with boolean algorithm
Methods:
    evaluation (src_auth, ext_auth):
        the evaluation algorithm
"""
class BooleanAuthorEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src_auth (list[Author]): Source Reference Author list
        ext_auth (list[Author]): External Reference Author list
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src_auth, ext_auth):
        if len(src_auth) == 0: # if source list is empty
            return 0.0
        for auth in src_auth:
            if auth not in ext_auth:
                return 0.0
        return 1.0

"""
Reference DOI component evaluation with boolean algorithm
Methods:
    evaluation (src_doi, ext_doi):
        the evaluation algorithm
"""
class BooleanDoiEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src_doi (str): Source Reference doi attribute
        ext_doi (str): External Reference doi attribute
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src_doi, ext_doi):
        if src_doi is None:
            return "N/A"
        else:
            return float(src_doi.lower() == ext_doi.lower())

"""
Reference date attribute evaluation with boolean algorithm
Methods:
    evaluation (src, ext):
        the evaluation algorithm
"""
class BooleanDateEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src (str): Source Reference date attribute
        ext (str): External Reference date attribute
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        else:
            return float(src.strip() == ext.strip())

"""
Reference pages attribute evaluation with boolean algorithm
Methods:
    evaluation (src_pages, ext_pages):
        the evaluation algorithm
"""
class BooleanPagesEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src_pages (str): Source Reference pages attribute
        ext_pages (str): External Reference pages attribute
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src_pages, ext_pages):
        if src_pages is None or ext_pages is None:
            return "N/A"
        else:
            return float(src_pages.strip() == ext_pages.strip())

"""
Reference volume attribute evaluation with boolean algorithm
Methods:
    evaluation (src, ext):
        the evaluation algorithm
"""
class BooleanVolumeEvaluator(BooleanEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src (str): Source Reference volume attribute
        ext (str): External Reference volume attribute
    Returns:
        float: Numerical representation of boolean true (1.0)/false (0.0)
    """
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        else:
            return float(src.strip() == ext.strip())

"""
Abstract class for Levenshtein evaluators
Methods:
    name:
        Returns the name of the evaluator
"""
class LevenshteinEvaluator(Evaluator):
    """
    Returns the name of the evaluator
    Parameters: None
    Returns:
        str: Name of the evaluation method (class name)
    """
    def name(self):
        return "levenshtein"

"""
Reference title attribute evaluation using Levenshtein algorithm
Methods:
    evaluation (src, ext):
        The evaluation algorithm
"""
class LevenshteinTitleEvaluator(LevenshteinEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src (str): Source Reference title attribute
        ext (str): External Reference title attribute
    Returns:
        float: Normalised similarity score between 0.0-1.0
    """
    def evaluation(self, src, ext):
        return rapidfuzz.distance.Levenshtein.normalized_similarity(utils.normalise_str(src), utils.normalise_str(ext))

"""
Reference date attribute evaluation using Levenshtein algorithm
Methods:
    evaluation (src, ext):
        The evaluation algorithm
"""
class LevenshteinDateEvaluator(LevenshteinEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src (str): Source Reference date attribute
        ext (str): External Reference date attribute
    Returns:
        float: Normalised similarity score between 0.0-1.0
    """
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        return rapidfuzz.distance.Levenshtein.normalized_similarity(src.strip(), ext.strip())

"""
Reference volume attribute evaluation using Levenshtein algorithm
Methods:
    evaluation (src, ext):
        The evaluation algorithm
"""
class LevenshteinVolumeEvaluator(LevenshteinEvaluator):
    """
    The evaluation algorithm
    Parameters:
        src (str): Source Reference volume attribute
        ext (str): External Reference volume attribute
    Returns:
        float: Normalised similarity score between 0.0-1.0
    """
    def evaluation(self, src, ext):
        if src is None or ext is None:
            return "N/A"
        return rapidfuzz.distance.Levenshtein.normalized_similarity(src.strip(), ext.strip())

# Dict of evaluators for each Reference attribute
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

"""
Manages evaluation inputs and outputs
Attributes:
    config(dict):
        JSON formatted dictionary for setting evaluation methods for attributes
Methods:
    evaluate_element(element, src_ref, ext_ref):
        Evaluates element using evaluation method specified in config
    aggregate(evaluations):
        Combines evaluation scores using a weighted average
    evaluate(src_ref, ext_ref):
        Evaluates attributes of a single Reference instance
"""
class EvaluationController:
    def __init__(self, config):
        self.config = config

    """
    Evaluates element using evaluation method specified in config
    Parameters:
        element (str): Name of the attribute to be evaluated
        src_ref (Reference): Source reference
        ext_ref (Reference): External reference
    Returns:
        dict: Formatted response with evaluation details
    """
    def evaluate_element(self, element, src_ref, ext_ref):
        src_elem = getattr(src_ref, element) # Gets attribute from Reference instance
        ext_elem = getattr(ext_ref, element)
        eval_weights = self.config[element]["evaluators"] # Retrieves method-weight key-value pair
        evaluations = []

        for method, weight in eval_weights.items():
            evaluator = evaluator_registry.get(element).get(method) # Gets specific evaluator for named element
            result = evaluator.evaluate(src_elem, ext_elem) # Calls the evaluators evaluate method
            result['weight'] = weight # Stores the weight in the results
            evaluations.append(result)

        if len(evaluations) == 1:
            score = evaluations[0]["score"] # Scores don't need aggregating if only one evaluator is utilised
        else:
            score = self.aggregate(evaluations)

        return {
            "score": score, # Total score of all evaluations of element combined
            "evaluation-method": evaluations
        }

    """
    Combines evaluation scores using a weighted average
    Parameters:
        evaluations (list[dict]): Collection of evaluation result dictionaries
    Returns:
        float: normalised weighted average of scores
    """
    def aggregate(self, evaluations):
        scores = []
        weights = []

        for e in evaluations:
            score = e['score']
            weight = e.get('weight', 1.0) # Defaults to 1.0 if no weight exists
            if isinstance(score, float): # Skips "N/A" strings
                scores.append(score)
                weights.append(weight)

        return fmean(scores, weights=weights) if weights else None

    """
    Evaluates attributes of a single Reference instance
    Parameters:
        src_ref (Reference): Source Reference
        ext_ref (Reference): External Reference
    Returns:
        dict: Nested dictionary of evaluation result strings
    """
    def evaluate(self, src_ref, ext_ref):
        results = {}
        for elem in self.config:
            results[elem] = self.evaluate_element(elem, src_ref, ext_ref)
        overall = all(results[elem]["score"] for elem in results) # overall combined score of all attribute scores

        return {"overall": overall, "reference element": results} # list of attributes and their evaluations


"""
Run full evaluator
Parameters:
    bibliography (BeautifulSoup): XML file of bibliography as soup parser object
    config (dict): Evaluation configuration
    mailto (str): Email address required for crossref api
    file_name (str): Name of output file (optional)
Returns:
    dict: all reference evaluations
"""
def evaluate_bibliography(bibliography, config, mailto, file_name=""):
    evaluator = EvaluationController(config) # Load evaluation settings onto controller
    parsed_bib = parser.XmlBibliography().parse(bibliography) # Parses into Reference objects
    results = []
    for ref in parsed_bib:
        search_results = crossref.CrossrefSearcher(mailto, 20).search(ref) # Initiates search
        if search_results is not None:
            found_ref = crossref.CrossrefParser().extract_ref(search_results)
            evaluation = evaluator.evaluate(ref, found_ref)
            results.append({'reference': ref, 'reference-located': found_ref, 'evaluation': evaluation})
        else:
            results.append({'reference': ref, 'reference-located': 'None Found', 'evaluation': 'None'}) # If no reference is found

    print("finished, returning results")
    utils.export_json(results, file_name + (" - " if len(file_name) > 0 else "") + "verification results") # exports results as JSON
    return results
