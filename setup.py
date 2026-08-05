#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages


def get_long_description():
    path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(path) as f:
        return f.read()


def get_version():
    import subprocess
    base = open("src/ansiblecmdb/data/VERSION", "r").read().strip()
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return "{0}+g{1}".format(base, git_hash)
    except Exception:
        return base


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    print("You should also add a git tag for this version:")
    print(" git tag {0}".format(get_version()))
    print(" git push --tags")
    sys.exit()

setup(
    name="ansible-cmdb",
    version=get_version(),
    license="GPLv3",
    description="Generate host overview from ansible fact gathering output",
    long_description=get_long_description(),
    url="https://github.com/fboender/ansible-cmdb",
    author="Ferry Boender",
    author_email="ferry.boender@electricmonk.nl",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    package_data={
        "ansiblecmdb": [
            "data/VERSION",
            "data/tpl/*",
            "data/static/js/*",
            "data/static/images/*",
        ]
    },
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["mako", "pyyaml", "ushlex", "jsonxs"],
    scripts=[
        "src/ansible-cmdb",
        "src/ansible-cmdb.py",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
