import setuptools
from pip._internal.download import PipSession
from pip._internal.req import parse_requirements

with open("README.md", "r") as fh:
    _LONG_DESCRIPTION = fh.read()

_INSTALL_REQS = parse_requirements('requirements.txt', session=PipSession())
_REQUIRES = [str(ir.req) for ir in _INSTALL_REQS]

setuptools.setup(
    name="url_metadata",
    version="0.0.1",
    author="Amen Souissi",
    author_email="amensouissi@ecreall.com",
    description="An URL metadata getter Flask micro website",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/assembl/url_metadata",
    packages=setuptools.find_packages(),
    license='AGPLv3',
    setup_requires=['pip>=6'],
    install_requires=_REQUIRES,
    package_data={
        'url_metadata': [
            'templates/*.html',
            'utils/providers.json',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
