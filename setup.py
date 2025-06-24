"""
Setup script for T-GUI.
"""

from setuptools import setup, find_packages

# Read README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A napari-like framework for building extensible GUI applications."

# Read requirements
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "PyQt5>=5.12.0",
        "pluggy>=1.0.0",
        "numpy>=1.18.0",
    ]

setup(
    name="t-gui",
    version="0.1.0",
    author="T-GUI Team",
    author_email="team@t-gui.org",
    description="A napari-like framework for building extensible GUI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/t-gui",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "pyside2": ["PySide2>=5.12.0"],
        "pyqt6": ["PyQt6>=6.0.0"],
        "pyside6": ["PySide6>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "t-gui=t_gui:run",
        ],
    },
    include_package_data=True,
    package_data={
        "t_gui": [
            "resources/icons/*.png",
            "resources/icons/*.svg",
        ],
    },
    keywords="gui framework plugin extensible napari qt",
    project_urls={
        "Bug Reports": "https://github.com/your-username/t-gui/issues",
        "Source": "https://github.com/your-username/t-gui",
        "Documentation": "https://t-gui.readthedocs.io/",
    },
)
