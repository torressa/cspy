import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cspy-torressa",
    version="0.0.1",
    description="A bidirectional algorithm for the Constrained Shortest Path",
    license="MIT",
    author="David Torres",
    author_email="d.torressanchez@lancs.ac.uk",
    keywords=["shortest path", "resource constrained shortest path",
              "bidirectional algorithm"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/torressa/cspy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
