import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="systemdlint",
    version="1.0.0",
    author="Konrad Weihmann",
    author_email="kweihmann@outlook.com",
    description="Systemd Unitfile Linter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/priv-kweihmann/systemdlint",
    packages=setuptools.find_packages(),
    install_requires=[
        'systemdunitparser>=0.1',
    ],
    scripts=['bin/systemdlint'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
)