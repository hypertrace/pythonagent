import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hypertrace-pythonagent",
    version="0.1.0",
    author="Robert C. Broeckelmann Jr.",
    author_email="robert@iyasec.io",
    description="The Hypertrace Python Agent",
    long_description="file: README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/Traceableai/pythonagent",
    project_urls={
        "Bug Tracker":"https://github.com/Traceableai/pythonagent/issues",
    },
    classifiers={
        "Programming Language :: Python :: 3",
        "License :: Apache",
        "Operating System :: OS Independent"
    }
    package_dir={"",: "hypertrace"}
    packages='setuptools.find_packages(where="hypertrace")',
    python_requires=">=3.7",
#    [options.packages.find],
#    where = src

)
