"""
docutools package.

Documentation tools for lc projects
"""
import os

# for apps on gevent we must patch early => Set that env variable:
# (see docs lp tips.md)
af = os.environ.get('async_framework')
if af == 'gevent':
    from gevent import monkey

    monkey.patch_all()

from typing import List

__all__: List[str] = []  # noqa: WPS410 (the only __variable__ we use)
