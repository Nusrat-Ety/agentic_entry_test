import json
import urllib.request
import urllib.error
from packaging.specifiers import SpecifierSet
from packaging.version import Version

PYTHON_VERSION = Version("3.11")
FILE_NAME = "requirements.txt"

not_found = []
incompatible = []
requirements = []

print("Script started...")

with open(FILE_NAME, "r") as file:
    lines = [line.strip() for line in file if line.strip()]

print(f"Dependencies loaded: {len(lines)}")

for line in lines:
    name, version = line.split("==")
    name = name.strip()
    version = version.strip()

    print(f"Checking {name}=={version}...")

    release_url = f"https://pypi.org/pypi/{name}/{version}/json"

    try:
        request = urllib.request.Request(
            release_url,
            headers={"User-Agent": "Python-Dependency-Checker"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)

        requires_python = data["info"].get("requires_python") or ""

        if requires_python:
            specifier = SpecifierSet(requires_python)

            for item in specifier:
                if item.operator in (">=", ">"):
                    requirements.append(
                        (Version(item.version), f"{name}=={version}")
                    )

            if not specifier.contains(PYTHON_VERSION):
                incompatible.append(f"{name}=={version}")

    except urllib.error.HTTPError as error:
        if error.code == 404:
            not_found.append(f"{name}=={version}")
        else:
            print(f"HTTP error: {error.code} for {name}")

    except Exception as error:
        print(f"Error checking {name}: {error}")

print("\nDependencies checked:", len(lines))
print("Not found on PYPI:", not_found)
print("Incompatible with python 3.11:", incompatible)

if requirements:
    highest = max(requirements, key=lambda x: x[0])
    print("Highest requirement:", highest[1], f"(>= {highest[0]})")
else:
    print("Highest requirement: None")