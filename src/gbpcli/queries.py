"""GraphQL query definitions"""
# Auto-generated: DO NOT EDIT
# pylint: disable=line-too-long,invalid-name
build = "query Build($name: String!, $number: Int!) {\n  build(name: $name, number: $number) {\n    name\n    number\n    keep\n    published\n    notes\n    submitted\n    completed\n    packagesBuilt {\n      cpv\n    }\n  }\n}\n"
builds = "query Builds($name: String!) {\n  builds(name: $name) {\n    name\n    number\n    submitted\n    completed\n    published\n    notes\n    keep\n  }\n}\n"
builds_with_packages = "query Builds($name: String!) {\n  builds(name: $name) {\n    name\n    number\n    submitted\n    completed\n    published\n    notes\n    keep\n    packagesBuilt {\n      cpv\n    }\n  }\n}\n"
create_note = "mutation CreateNote($name: String!, $number: Int!, $note: String) {\n  createNote(name: $name, number: $number, note: $note) {\n    notes\n  }\n}\n"
diff = "query Diff($left: BuildInput!, $right: BuildInput!) {\n  diff(left: $left, right: $right) {\n    left {\n      name\n      number\n      submitted\n    }\n    right {\n      name\n      number\n      submitted\n    }\n    items {\n      item\n      status\n    }\n  }\n}\n"
keep_build = "mutation KeepBuild($name: String!, $number: Int!) {\n  keepBuild(name: $name, number: $number) {\n    keep\n  }\n}\n"
latest = "query Latest($name: String!) {\n  latest(name: $name) {\n    number\n  }\n}\n"
logs = "query Build($name: String!, $number: Int!) {\n  build(name: $name, number: $number) {\n    logs\n  }\n}\n"
machines = "query {\n  machines {\n    name\n    builds\n  }\n}\n"
packages = "query Packages($name: String!, $number: Int!) {\n  packages(name: $name, number: $number)\n}\n"
publish = "mutation Publish($name: String!, $number: Int!) {\n  publish(name: $name, number: $number) {\n    publishedBuild {\n      number\n    }\n  }\n}\n"
pull = "mutation Pull($name: String!, $number: Int!) {\n  pull(name: $name, number: $number) {\n    builds\n  }\n}\n"
release_build = "mutation ReleaseBuild($name: String!, $number: Int!) {\n  releaseBuild(name: $name, number: $number) {\n    keep\n  }\n}\n"
schedule_build = (
    "mutation ScheduleBuild($name: String!) {\n  scheduleBuild(name: $name)\n}\n"
)
search_notes = "query SearchNotes($name: String!, $key: String!) {\n  searchNotes(name: $name, key: $key) {\n    name\n    number\n    keep\n    published\n    notes\n    submitted\n    completed\n  }\n}\n"
