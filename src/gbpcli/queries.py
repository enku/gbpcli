"""GraphQL query definitions"""
# Auto-generated: DO NOT EDIT
# pylint: disable=line-too-long,invalid-name
build = "query ($id: ID!) {\n  build(id: $id) {\n    id\n    machine\n    keep\n    published\n    notes\n    submitted\n    completed\n    packagesBuilt {\n      cpv\n    }\n  }\n}\n"
builds = "query ($name: String!) {\n  builds(name: $name) {\n    id\n    machine\n    submitted\n    completed\n    published\n    notes\n    keep\n  }\n}\n"
builds_with_packages = "query ($name: String!) {\n  builds(name: $name) {\n    id\n    machine\n    submitted\n    completed\n    published\n    notes\n    keep\n    packagesBuilt {\n      cpv\n    }\n  }\n}\n"
create_note = "mutation ($id: ID!, $note: String) {\n  createNote(id: $id, note: $note) {\n    notes\n  }\n}\n"
diff = "query ($left: ID!, $right: ID!) {\n  diff(left: $left, right: $right) {\n    left {\n      id\n      machine\n      submitted\n    }\n    right {\n      id\n      machine\n      submitted\n    }\n    items {\n      item\n      status\n    }\n  }\n}\n"
keep_build = "mutation ($id: ID!) {\n  keepBuild(id: $id) {\n    keep\n  }\n}\n"
latest = "query ($name: String!) {\n  latest(name: $name) {\n    id\n  }\n}\n"
logs = "query ($id: ID!) {\n  build(id: $id) {\n    logs\n  }\n}\n"
machines = "query {\n  machines {\n    name\n    buildCount\n  }\n}\n"
packages = "query ($id: ID!) {\n  build(id: $id) {\n    packages\n  }\n}\n"
publish = "mutation ($id: ID!) {\n  publish(id: $id) {\n    publishedBuild {\n      id\n    }\n  }\n}\n"
pull = "mutation ($id: ID!) {\n  pull(id: $id) {\n    buildCount\n  }\n}\n"
release_build = "mutation ($id: ID!) {\n  releaseBuild(id: $id) {\n    keep\n  }\n}\n"
schedule_build = "mutation ($name: String!) {\n  scheduleBuild(name: $name)\n}\n"
search_notes = "query ($name: String!, $key: String!) {\n  searchNotes(name: $name, key: $key) {\n    id\n    machine\n    keep\n    published\n    notes\n    submitted\n    completed\n    packagesBuilt {\n      cpv\n    }\n  }\n}\n"
