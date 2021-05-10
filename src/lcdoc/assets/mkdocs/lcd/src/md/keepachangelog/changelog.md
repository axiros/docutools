# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [CalVer Versioning](http://calver.org) ![](https://img.shields.io/badge/calver-YYYY.0M.0D-22bfda.svg)

{% for version in changelog.versions_list -%}
{% include 'version.md' with context %}
{% endfor -%}
