from setuptools import find_packages, setup

github = "https://github.com/aj3423/protod/"

setup(
    name             = "protod",
    version          = "23.11.11",
    description      = "Decode protobuf without message definition.",
    url              = github,
    author           = "aj3423",
    packages         = find_packages(),
    install_requires = [
        'chardet',
        'protobuf',
        'termcolor'
    ],
    entry_points={
        "console_scripts": [
            "protod=protod.main:dummy"
        ]
    },

    long_description = "See: " + github
)