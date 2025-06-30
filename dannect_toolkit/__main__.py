#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Main Entry Point
모듈 실행 진입점: python -m dannect_toolkit
"""

import sys
from .cli.main import main

if __name__ == "__main__":
    sys.exit(main()) 