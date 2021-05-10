#!/usr/bin/env python
"""
Passthrough to Standard Mkdocs

"""
import os, sys


def main():
    if sys.argv[0] != __file__:
        sys.argv.pop(1)
    sys.exit(os.system('mkdocs %s' % ' '.join(sys.argv[1:])))


if __name__ == '__main__':
    main()
