"""
docutools package.

Documentation tools for lc projects
"""
import os, sys

# for apps on gevent we must patch early => Set that env variable:
# (see docs lp tips.md)
_ = os.environ.get
af, tp = _('async_framework'), _('try_preload', '')
if af == 'gevent' or 'gevent' in tp:
    try:
        from gevent import monkey

        monkey.patch_all()
        from lcdoc.lp import Raiser

        if 'serve' in sys.argv:
            # gevent hangs with the live reload server on exceptions. So, hammer:
            Raiser.die = lambda msg: os.kill(os.getpid(), 15)
    except ImportError:
        pass

from typing import List

__all__: List[str] = []  # noqa: WPS410 (the only __variable__ we use)
