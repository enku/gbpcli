"""Abstraction of the Gentoo Build Publisher API"""

# mypy: disable-error-code="attr-defined"
import warnings
from typing import Any, cast

import yarl

from gbpcli import config, graphql
from gbpcli.types import Build, Change, ChangeState, SearchField


class GBP:
    """Python wrapper for the Gentoo Build Publisher API"""

    def __init__(self, url: str, *, auth: config.AuthDict | None = None) -> None:
        self.query = graphql.Queries(yarl.URL(url) / "graphql", auth=auth)

    def machines(
        self, *, names: list[str] | None = None
    ) -> list[tuple[str, int, dict[str, Any]]]:
        """Handler for subcommand"""
        data = graphql.check(self.query.gbpcli.machines(names=names))

        return [
            (i["machine"], i["buildCount"], i["latestBuild"]) for i in data["machines"]
        ]

    def machine_names(self) -> list[str]:
        """Return the list of machine names

        Machines having builds.
        """
        machines = graphql.check(self.query.gbpcli.machine_names())["machines"]

        return [machine["machine"] for machine in machines]

    def publish(self, build: Build) -> None:
        """Publish the given build"""
        graphql.check(self.query.gbpcli.publish(id=build.id))

    def pull(
        self, build: Build, *, note: str | None = None, tags: list[str] | None = None
    ) -> None:
        """Pull the given build"""
        graphql.check(self.query.gbpcli.pull(id=build.id, note=note, tags=tags))

    def latest(self, machine: str) -> Build | None:
        """Return the latest build for machine

        Return None if there are no builds for the given machine
        """
        data = graphql.check(self.query.gbpcli.latest(machine=machine))

        if data["latest"] is None:
            return None

        build_id = data["latest"]["id"]
        return Build.from_id(build_id)

    def resolve_tag(self, machine: str, tag: str) -> Build | None:
        """Return the build of the given machine & tag"""
        data = graphql.check(self.query.gbpcli.resolve_tag(machine=machine, tag=tag))[
            "resolveBuildTag"
        ]

        if data is None:
            return None

        build_id = data["id"]

        return Build.from_id(build_id)

    def builds(self, machine: str, *, with_packages: bool = False) -> list[Build]:
        """Return a list of Builds for the given machine"""
        builds = reversed(
            self.query.gbpcli.builds(machine=machine, withPackages=with_packages)[0][
                "builds"
            ]
        )

        return [Build.from_api_response(i) for i in builds]

    def diff(
        self, machine: str, left: int, right: int
    ) -> tuple[Build, Build, list[Change]]:
        """Return difference between two builds"""
        data = graphql.check(
            self.query.gbpcli.diff(left=f"{machine}.{left}", right=f"{machine}.{right}")
        )

        return (
            Build.from_api_response(data["diff"]["left"]),
            Build.from_api_response(data["diff"]["right"]),
            [
                Change(item=i["item"], status=getattr(ChangeState, i["status"]))
                for i in data["diff"]["items"]
            ],
        )

    def logs(self, build: Build) -> str | None:
        """Return logs for the given Build"""
        data = graphql.check(self.query.gbpcli.logs(id=build.id))

        return None if data["build"] is None else data["build"]["logs"]

    def get_build_info(self, build: Build) -> Build | None:
        """Return build with info gained from the GBP API"""
        data, errors = self.query.gbpcli.build(id=build.id)

        if (build := data["build"]) is None:
            if errors:
                raise graphql.APIError(errors, data)
            return None

        return Build.from_api_response(build)

    def build(self, machine: str, *, is_repo=False, **params: Any) -> str:
        """Schedule a build"""
        build_params = [{"name": key, "value": value} for key, value in params.items()]
        api_response = graphql.check(
            self.query.gbpcli.schedule_build(
                machine=machine,
                params=build_params,
                **({"isRepo": True} if is_repo else {}),
            )
        )
        return cast(str, api_response["scheduleBuild"])

    def packages(self, build: Build) -> list[str] | None:
        """Return the list of packages for a build"""
        data = graphql.check(self.query.gbpcli.packages(id=build.id))["build"]
        return data and cast(list[str] | None, data.get("packages"))

    def keep(self, build: Build) -> dict[str, bool]:
        """Mark a build as kept"""
        return cast(
            dict[str, bool],
            graphql.check(self.query.gbpcli.keep_build(id=build.id))["keepBuild"],
        )

    def release(self, build: Build) -> dict[str, bool]:
        """Unmark a build as kept"""
        return cast(
            dict[str, bool],
            graphql.check(self.query.gbpcli.release_build(id=build.id))["releaseBuild"],
        )

    def create_note(self, build: Build, note: str | None) -> dict[str, str]:
        """Create or delete note for the given build.

        If note is None, the note is deleted (if it exists).
        """
        return cast(
            dict[str, str],
            graphql.check(self.query.gbpcli.create_note(id=build.id, note=note))[
                "createNote"
            ],
        )

    def search(self, machine: str, field: SearchField, key: str) -> list[Build]:
        """Search builds for the given machine name in fields containing key.

        Return a list of Builds who's given field match the (case-insensitive) string.
        """
        api_response = graphql.check(
            self.query.gbpcli.search(machine=machine, field=field.value, key=key)
        )
        builds = api_response["search"]

        return [Build.from_api_response(i) for i in builds]

    def search_notes(self, machine: str, key: str) -> list[Build]:
        """Search builds for the given machine name for notes containing key.

        This method is deprecated. Use search() instead.
        """
        message = "This method is deprecated. Use search() instead"
        warnings.warn(message, DeprecationWarning, stacklevel=2)

        return self.search(machine, SearchField.notes, key)

    def tag(self, build: Build, tag: str) -> None:
        """Add the given tag to the build"""
        graphql.check(self.query.gbpcli.tag_build(id=build.id, tag=tag))

    def untag(self, machine: str, tag: str) -> None:
        """Remove the tag from the given machine"""
        graphql.check(self.query.gbpcli.untag_build(machine=machine, tag=tag))
