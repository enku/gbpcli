"""noxfile for ci/cd testing"""

# pylint: disable=missing-docstring
import nox

PYTHON_VERSIONS = (
    "3.12",
    "3.13",
    # "3.14", PyO3 (needed to build orjson) does not support 3.14 yet
)


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    session.install(".")
    dev_dependencies = nox.project.load_toml("pyproject.toml")["dependency-groups"][
        "dev"
    ]
    session.install(*dev_dependencies)

    session.run("coverage", "run", "-m", "tests")
    session.run("pdm", "run", "make", "lint", external=True)
    session.run("coverage", "report")
