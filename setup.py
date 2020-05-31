import setuptools
import subprocess

with open("README.md", "r") as fh:
    long_description = fh.read()

gitcommand = subprocess.run(["git", "describe", "--always"], stdout=subprocess.PIPE, universal_newlines=True)
version = gitcommand.stdout.strip("\n")

setuptools.setup(
    name="scrapec",
    version=version,
    author="Scraterpreter Authors",
    author_email="contact@paullee.dev",
    description="Scrapec is a program that compiles .sb3 files into .scrape files, which can then be run using Scrape.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scraterpreter/scrapec",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Compilers",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'scrapec = src.scrapec:main',
        ],
    },
)

