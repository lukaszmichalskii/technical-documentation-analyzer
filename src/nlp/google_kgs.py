"""Google Knowledge Graph Search

Standalone script allows the user to query google knowledge graph for particular keyword
Used in NER (Named Entity Recognition) part
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from typing import List, Tuple, Any, Dict

# config
REQUEST_DEPTH_LIMIT = 100000

# filters
ROOT = "itemListElement"
DESC_KEY = "detailedDescription"
NER = "@type"
RESULT_KEY = "result"
URL_KEY = "url"
ARTICLE_BODY = "articleBody"


class GoogleSearchError(Exception):
    pass


def google_search(
    query, limit=1, indent=True, ner=True
) -> Tuple[List[Any], List[Any], List[Any]] | Dict[Any]:
    """
    Search Google Knowledge Graph utility method
    Args:
        query: keyword to search
        limit: requests depth limit
        indent: response json formatting
        ner: flag for NER data classification
    Returns:
        Response from graph in raw json form or tuple ready to assembly in NER NLP
    """
    api_key = os.environ.get("API_KEY")
    params = google_api_params(query=query, api_key=api_key, limit=limit, indent=indent)
    url = build_url(params)
    response = do_GET(url)

    if ner:
        return classify(response)
    return response


def google_api_params(**kwargs) -> Dict[str, Any]:
    return {
        "query": kwargs.get("query"),
        "limit": int(kwargs.get("limit", 10)),
        "indent": kwargs.get("indent", True),
        "key": kwargs.get("api_key"),
    }


def build_url(params: Dict[str, Any]) -> str:
    service_url = "https://kgsearch.googleapis.com/v1/entities:search"
    url = service_url + "?" + urllib.parse.urlencode(params)
    return url


def do_GET(url) -> Dict[str, Dict]:
    try:
        response = json.loads(urllib.request.urlopen(url).read())
        return response
    except urllib.error.HTTPError as e:
        raise GoogleSearchError(e)


def classify(response) -> Tuple[List[Any], List[Any], List[Any]]:
    text_ls = []
    node_label_ls = []
    url_ls = []

    for element in response[ROOT]:
        named_entities(element, node_label_ls)
        description(element, text_ls)
        find_url(element, url_ls)

    return text_ls, node_label_ls, url_ls


def named_entities(element, storage_reference) -> None:
    try:
        storage_reference.append(element[RESULT_KEY][NER])
    except Exception:
        storage_reference.append("")


def find_url(element, storage_reference) -> None:
    try:
        storage_reference.append(element[RESULT_KEY][DESC_KEY][URL_KEY])
    except Exception:
        storage_reference.append("")


def description(element, storage_reference) -> None:
    try:
        storage_reference.append(element[RESULT_KEY][DESC_KEY][ARTICLE_BODY])
    except Exception:
        storage_reference.append("")


def help_() -> str:
    return """
Exit codes:
    0 - successful execution
    1 - error during GET request to Google resources
    2 - requests limit overflow
    3 - API_KEY env not provided

Environment variables:
    LIMIT   : Google Knowledge Graph per user search limit (per day limit 100 000).
              Default: 1
    API_KEY : Google Knowledge Graph private api key, required for sending GET requests.
Examples:
    Search for 'nlp' entity in graph with raw json response
    export API_KEY=private_api_key
    python google_kgs.py --query nlp
    Search for 'nlp' entity in graph with classified data for named entity recognition
    export API_KEY=private_api_key
    python google_kgs.py --query nlp --ner
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        required=True,
        help="Keyword to search in google knowledge graph API",
    )
    parser.add_argument(
        "--ner", action="store_true", help="Classify data from json response to NER"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force query even if free tier exceeded."
    )
    parser.epilog = help_()
    args = parser.parse_args()

    limit = int(os.environ.get("LIMIT", 1))
    if limit >= REQUEST_DEPTH_LIMIT and not args.force:
        print(
            'Google Knowledge Graph API free tier exceeded. Use "--force" to override.'
        )
        return 2
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        print(
            "API_KEY environment variable required for Google Knowledge Graph requests"
        )
        return 3
    if args.force:
        print(
            "Free tier override, service might work incorrectly e.g. block account for spamming (bot protection)"
        )

    try:
        response = google_search(args.query, limit, ner=args.ner)
        print(response)
    except GoogleSearchError as e:
        print(str(e))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
