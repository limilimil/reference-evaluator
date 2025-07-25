# Reference Evaluator

## Requirements
- Python 3.12
- [Grobid 0.8.2](https://github.com/kermitt2/grobid) (PDF parsing only)
- Docker (For Grobid)

## Installation:
```
git clone https://github.com/limilimil/reference-evaluator

pip install -r requirements.txt
```
[For Grobid and Docker, see the Grobid documentation](https://grobid.readthedocs.io/)

## To Run:

### PDF parsing:
```
# docker terminal
docker run -t --rm -p 8070:8070 grobid/grobid:0.8.2

# python
parser.PdfToXML(input_path, output_path, grobid_config)
```
### Reference evaluator:
```
evaluation.evaluate_bibliography(bibliography, config, mailto, file_name)

```
#### Parameters:
- bibliography (BeautifulSoup): XML file of bibliography as soup parser object
- config (dict): Evaluation configuration ([see example-config.json](https://github.com/limilimil/reference-evaluator/blob/main/example-config.json))
- mailto (str): Email address required for crossref api
- file_name (str): Name of output file (optional)


