#!/usr/bin/env python3
"""
PyKRX MCP 서버 실행 스크립트
"""

import sys
import os
import asyncio

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import main

if __name__ == "__main__":
    asyncio.run(main())
