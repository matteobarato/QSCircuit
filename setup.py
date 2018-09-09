import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QSCircuit",
    version="0.0.1",
    author="Matteo Barato",
    author_email="matteo.barato@studio.unibo.it",
    description="QSCircuit package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/example-project",
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
          'pyparsing',
     ],
    scripts=['bin/QSCircuit'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
