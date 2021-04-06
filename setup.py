import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="net_node",
    version="0.0.1",
    author="Solovyev Yurii",
    author_email="solovyev.yurii@gmail.com",
    description="The package for network devicses cli automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JurgenOS/net_node",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "setuptools>=42",
        "wheel",
        "paramiko",
        "pysnmp",
        "chardet",
    ],
)
