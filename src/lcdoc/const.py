import time

AttrDict = dict

# class AttrDict(dict):
#     def __getattr__(self, k):
#         self[k] = 0
#         return 0


Stats = AttrDict()
PageStats = {}
LogStats = {}

now_ms = lambda: int(time.time() * 1000)
t0 = [now_ms()]


lprunner_sep = ['<!-- lprunner -->']
