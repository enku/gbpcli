"""noxfile for ci/cd testing"""

# pylint: disable=missing-docstring
import nox


@nox.session(python=("3.11", "3.12", "3.13", "3.14"))
def tests(session: nox.Session) -> None:
    session.install(".")
    dev_dependencies = nox.project.load_toml("pyproject.toml")["dependency-groups"][
        "dev"
    ]
    session.install(*dev_dependencies)

    session.run("pdm", "run", "make", "test", external=True)
    session.run("pdm", "run", "make", "lint", external=True)
    session.run("coverage", "report")
