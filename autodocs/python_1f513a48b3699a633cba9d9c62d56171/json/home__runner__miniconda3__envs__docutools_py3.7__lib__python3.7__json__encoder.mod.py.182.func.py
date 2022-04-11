def encode(self, o):
    """Return a JSON string representation of a Python data structure.

    >>> from json.encoder import JSONEncoder
    >>> JSONEncoder().encode({"foo": ["bar", "baz"]})
    '{"foo": ["bar", "baz"]}'

    """
    # This is for extremely simple cases and benchmarks.
    if isinstance(o, str):
        if self.ensure_ascii:
            return encode_basestring_ascii(o)
        else:
            return encode_basestring(o)
    # This doesn't pass the iterator directly to ''.join() because the
    # exceptions aren't as detailed.  The list call should be roughly
    # equivalent to the PySequence_Fast that ''.join() would do.
    chunks = self.iterencode(o, _one_shot=True)
    if not isinstance(chunks, (list, tuple)):
        chunks = list(chunks)
    return ''.join(chunks)