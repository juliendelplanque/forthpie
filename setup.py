import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="forthpie",
    version="0.0.1",
    author="Julien Delplanque",
    description="A Forth written in Python for learning purpose.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juliendelplanque/forthpie",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)