from setuptools import setup
import moviedemo
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='moviedemo',
    version=moviedemo.__version__,
    packages=['moviedemo'],
    url='https://github.com/mminichino/movie-embeddings-demo',
    license='MIT License',
    author='Michael Minichino',
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'data_load = moviedemo.data_load:main',
            'demo_server = moviedemo.demo_server:main',
            'index_lookup = moviedemo.index_lookup:main',
            'generate_source_data = moviedemo.generate_source_data:main',
        ]
    },
    package_data={'moviedemo': ['templates/*', 'images/*']},
    install_requires=[
        "requests>=2.31.0",
        "aiohttp>=3.9.1",
        "certifi>=2023.7.22",
        "python-certifi-win32>=1.6.1",
        "google-cloud-aiplatform>=1.43.0",
        "google-api-core>=2.4.0",
        "google-api-python-client>=2.34.0",
        "cbcmgr>=2.2.18",
        "pillow>=10.2.0",
        "bumpversion>=0.6.0",
        "couchbase>=4.2.0",
        "python-daemon>=3.0.0",
        "Jinja2>=3.0.0",
        "Flask>=3.0.2",
        "waitress>=3.0.0"
    ],
    author_email='info@unix.us.com',
    description='Vector Search Demo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=["couchbase", "nosql", "vector", "search", "database"],
    classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Topic :: Database",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"],
)
