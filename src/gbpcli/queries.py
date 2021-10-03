"""GraphQL query definitions"""
# Auto-generated: DO NOT EDIT
# pylint: disable=line-too-long,invalid-name
build = "query Build($name: String!, $number: Int!) {\n  build(name: $name, number: $number) {\n    name\n    number\n    keep\n    published\n    notes\n    submitted\n    completed\n  }\n}\n"
builds = "query Builds($name: String!) {\n  builds(name: $name) {\n    name\n    number\n    submitted\n    completed\n    published\n    notes\n    keep\n  }\n}\n"
diff = "query Diff($left: BuildInput!, $right: BuildInput!) {\n  diff(left: $left, right: $right) {\n    left {\n      name\n      number\n      submitted\n    }\n    right {\n      name\n      number\n      submitted\n    }\n    items {\n      item\n      status\n    }\n  }\n}\n"
latest = "query Latest($name: String!) {\n  latest(name: $name) {\n    number\n  }\n}\n"
logs = "query Build($name: String!, $number: Int!) {\n  build(name: $name, number: $number) {\n    logs\n  }\n}\n"
machines = "query {\n  machines {\n    name\n    builds\n  }\n}\n"
packages = "query Packages($name: String!, $number: Int!) {\n  packages(name: $name, number: $number)\n}\n"
publish = "mutation Publish($name: String!, $number: Int!) {\n  publish(name: $name, number: $number) {\n    publishedBuild {\n      number\n    }\n  }\n}\n"
schedule_build = (
    "mutation ScheduleBuild($name: String!) {\n  scheduleBuild(name: $name)\n}\n"
)
