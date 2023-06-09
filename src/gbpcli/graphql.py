"""graphql library for gbpcli"""
from importlib import resources
from typing import Any

import requests
import yarl


class APIError(Exception):
    """When an error is returned by the REST API"""

    def __init__(self, errors, data) -> None:
        super().__init__(errors)
        self.data = data


class Query:
    """Interface to a graphql query.

    It can be called as a normal Python function.

    For example::

        >>> qs = "query ($machine: String!) { latest(machine: $machine) { id } }"
        >>> query = Query(qs, "https://gbp/graphql", requests.Session())
        >>> query(machine="lighthouse")
        ({'latest': {'id': 'lighthouse.14205'}}, None)
    """

    headers = {"Accept-Encoding": "gzip, deflate"}

    def __init__(self, query: str, url, session) -> None:
        self.query = query
        self.session = session
        self.url = str(url)

    def __str__(self) -> str:
        return self.query

    def __call__(self, **kwargs: Any) -> tuple[dict, dict]:
        json = {"query": self.query, "variables": kwargs}

        response = self.session.post(self.url, json=json, headers=self.headers)

        response.raise_for_status()
        response_json = response.json()

        return response_json.get("data"), response_json.get("errors")


class Queries:
    """Python interface to raw queries/*.graphql files"""

    def __init__(self, url: yarl.URL, distribution: str = "gbpcli") -> None:
        """A namespace for queries.

        url: the url to the graphql endpoint
        distribution: name of python package to search for queries/*.graphql files
        """
        self._url = str(url)
        self._session = requests.Session()
        self._distribution = distribution

    def __getattr__(self, name: str) -> Query:
        query_file = resources.files(self._distribution) / "queries" / f"{name}.graphql"
        try:
            query_str = query_file.read_text(encoding="UTF-8")
        except FileNotFoundError:
            raise AttributeError(name) from None

        return Query(query_str, self._url, self._session)

    def to_dict(self) -> dict[str, str]:
        """Return the queries as a dict"""
        files = (resources.files(self._distribution) / "queries").iterdir()

        return {
            filename.name[:-8]: getattr(self, filename.name[:-8])
            for filename in files
            if filename.name.endswith(".graphql")
        }


def check(query_result: tuple[dict, dict]) -> dict:
    """Run query and raise exception if there are errors"""
    data, errors = query_result

    if errors:
        raise APIError(errors, data)
    return data
