import time

Stats = {}
PageStats = {}
LogStats = {}

now_ms = lambda: int(time.time() * 1000)
t0 = [now_ms()]
