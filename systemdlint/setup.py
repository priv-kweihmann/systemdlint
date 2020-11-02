import setuptools

import subprocess
_long_description = "See https://github.com/priv-kweihmann/systemdlint for documentation"
_long_description_content_type = "text/plain"
try:
    _long_description = subprocess.check_output(["pandoc", "--from", "markdown", "--to", "rst", "../README.md"]).decode("utf-8")
    _long_description_content_type = "text/x-rst"
except (subprocess.CalledProcessError, FileNotFoundError):
    pass

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="systemdlint",
    version="1.1.14",
    author="Konrad Weihmann",
    author_email="kweihmann@outlook.com",
    description="Systemd Unitfile Linter",
    long_description=_long_description,
    long_description_content_type=_long_description_content_type,
    url="https://github.com/priv-kweihmann/systemdlint",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "systemdlint = systemdlint.__main__:main",
        ]
    },
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
