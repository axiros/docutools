# Evaluation and Caching

!!! note
    Understanding and controlling when blocks are evaluated is important for the **author** of docsets, (not the reader.


## Hashing

When the plugin identifies and parses lp blocks within your docset, it builds a hash to identify
them.

The hash is built over the body plus a specific set of header parameters:

```python lp mode=shsrc delim=hashed_headers dir=src
```

