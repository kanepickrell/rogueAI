from setuptools import setup, find_packages

setup(
    name="rogueai",
    version="0.1.0",
    description="A RAG-based chatbot for training event analysis",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "streamlit",
        "numpy",
        "pandas",
        "pathlib",
        "python-dotenv",
        "pyyaml",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'black>=22.0',
            'flake8>=4.0',
        ],
        'ml': [
            'torch',
            'transformers',
            'sentence-transformers',
            'scikit-learn',
        ]
    },
)