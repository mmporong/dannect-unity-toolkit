#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Setup
패키지 설치 설정
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dannect-unity-toolkit",
    version="2.0.0",
    author="Dannect",
    author_email="mmporong@gmail.com",
    description="범용 Unity 개발 자동화 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmporong/unity-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dannect-toolkit=dannect_toolkit.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="unity, automation, cli, webgl, build, git",
    project_urls={
        "Bug Reports": "https://github.com/mmporong/unity-toolkit/issues",
        "Source": "https://github.com/mmporong/unity-toolkit",
        "Documentation": "https://github.com/mmporong/unity-toolkit/blob/main/README.md",
    },
) 