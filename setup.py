from setuptools import setup, find_packages

setup(
    name="treehut-trend-analysis",
    version="0.1.0",
    description="Social media trend analysis tool for Treehut's Instagram presence",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.3",
        "nltk>=3.8.1",
        "spacy>=3.7.2",
        "plotly>=5.18.0",
        "dash>=2.14.0",
        "scikit-learn>=1.3.0",
        "python-dotenv>=1.0.0",
        "numpy>=2.0.0,<2.1.0",
        "matplotlib>=3.7.2",
        "seaborn>=0.12.2"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "treehut-analyze=src.main:main",
        ],
    },
) 