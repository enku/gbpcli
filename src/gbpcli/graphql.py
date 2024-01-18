"""graphql library for gbpcli"""
from functools import cache
from importlib import metadata, resources
from typing import Any

import requests
import yarl


class APIError(Exception):
    """When an error is returned by the REST API"""

    def __init__(self, errors: dict[str, Any], data: dict[str, Any]) -> None:
        super().__init__(errors)
        self.data = data


class Query:
    """Interface to a graphql query.

    It can be called as a normal Python function.

    For example::

        >>> qs = "query ($machine: String!) { latest(machine: $machine) { id } }"
        >>> query = Query(qs, "https://gbp/graphql", requests.Session())
        >>> query(machine="lighthouse")  # doctest: +ELLIPSIS
        ({'latest': {'id': 'lighthouse...'}}, {})
    """

    headers = {"Accept-Encoding": "gzip, deflate"}

    def __init__(
        self, query: str, url: yarl.URL | str, session: requests.Session
    ) -> None:
        self.query = query
        self.session = session
        self.url = str(url)

    def __str__(self) -> str:
        return self.query

    def __call__(self, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        json = {"query": self.query, "variables": kwargs}

        http_response = self.session.post(self.url, json=json, headers=self.headers)

        http_response.raise_for_status()
        query_result = http_response.json()

        return query_result.get("data", {}), query_result.get("errors", {})


class DistributionQueries:
    """Queries for a given distribution"""

    def __init__(self, url: str, distribution: str, session: requests.Session) -> None:
        # We want to make sure we explicitly raise an exception if this distribition
        # does not exist
        try:
            self._files = resources.files(distribution)
        except ModuleNotFoundError as error:
            raise error from None

        self._url = url
        self._distribution = distribution
        self._session = session

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.url!r}, {self._distribution!r}, ...)"

    # The CLI is a short-lived process so we're not concerned about cache size
    @cache  # pylint: disable=method-cache-max-size-none
    def __getattr__(self, name: str) -> Query:
        query_file = self._files / "queries" / f"{name}.graphql"

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


class Queries:  # pylint: disable=too-few-public-methods
    r"""Python interface to raw queries/*.graphql files

    This allows you to execute GraphQL queries as if they were Python methods. Queries
    appear in a namespace determined by which (Python) distribution they are defined in.
    For example the GraphQL queries defined in the "gbpcli" distribution are called
    "gbpcli.<query>":

        >>> q = Queries(yarl.URL("http://gbp/invalid"))
        >>> q.gbpcli.latest # doctest: +ELLIPSIS
        <graphql.Query object at 0x...>
        >>> str(q.gbpcli.latest)
        'query ($machine: String!) {\n  latest(machine: $machine) {\n    id\n  }\n}\n'
    """

    def __init__(self, url: yarl.URL) -> None:
        """A namespace for queries.

        url: the url to the graphql endpoint
        """
        self._url = str(url)
        self._session = requests.Session()
        self._session.headers["User-Agent"] = f"gbpcli/{metadata.version('gbpcli')}"

    @cache  # pylint: disable=method-cache-max-size-none
    def __getattr__(self, name: str) -> DistributionQueries:
        try:
            return DistributionQueries(self._url, name, self._session)
        except ModuleNotFoundError:
            raise AttributeError(name) from None


def check(query_result: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """Raise exception if there are errors in the query_result

    Otherwise return the data portion of the query_result.
    """
    data, errors = query_result

    if errors:
        raise APIError(errors, data)
    return data
