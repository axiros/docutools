<!-- AUTOMATICALLY GENERATED FILE - DO NOT DIRECTLY EDIT!

Direct edits will be gone after next CI build.
By: gk@axgk (Wed Aug 11 16:06:00 2021)
Command Line (see duties.py):

    /home/gk/miniconda3/envs/docutools_py37/bin/doc pre_process \
     --fail_on_blacklisted_words \
     --patch_mkdocs_filewatch_ign_lp \
     --gen_theme_link \
     --gen_last_modify_date \
     --gen_change_log \
     --gen_credits_page \
     --gen_auto_docs \
     --lit_prog_evaluation=md \
     --lit_prog_evaluation_timeout=5 \
     --lit_prog_on_err_keep_running=false
-->

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

This project adheres to [CalVer Versioning](http://calver.org) ![](https://img.shields.io/badge/calver-YYYY.M.D-22bfda.svg).

## [2021.9.0](https://github.com/AXGKl/docutools/releases/tag/2021.9.0)
<small>[Compare with 2021.8.9](https://github.com/AXGKl/docutools/compare/2021.8.9...2021.9.0)</small>

### Features
- Checking blacklisted words ([e7d258f](https://github.com/AXGKl/docutools/commit/e7d258f481cf7600ba85f55dfc38f8082c01eaf6) by Gunther Klessinger).
- Checking skip syntax and allowing commented lines w/o expect= ([51af4a1](https://github.com/AXGKl/docutools/commit/51af4a1457efe5d706aba869981a9760bee0ec93) by Gunther Klessinger).
- Page level header args with `page lp foo=bar` ([71ec316](https://github.com/AXGKl/docutools/commit/71ec316fa01ae66c42566e7c8baf13e2089e708d) by Gunther Klessinger).
- Supporting make_file and read_file also with session ([4561097](https://github.com/AXGKl/docutools/commit/45610976eb7b67aa191b61e8fa38d3e0d1b7bc9e) by Gunther Klessinger).


## [2021.8.9](https://github.com/AXGKl/docutools/releases/tag/2021.8.9)
<small>[Compare with 2021.8.3](https://github.com/AXGKl/docutools/compare/2021.8.3...2021.8.9)</small>

### Bug Fixes
- Json detection save for ini files ([c11fac7](https://github.com/AXGKl/docutools/commit/c11fac7ac3440bcdf5e5a72ef143e56c63b8b227) by Gunther Klessinger).
- No locks when skipped ([67490ad](https://github.com/AXGKl/docutools/commit/67490ad7364795fa287f18ad615e33470e2b9a7c) by Gunther Klessinger).

### Features
- Better stats ([3aa56ae](https://github.com/AXGKl/docutools/commit/3aa56ae55f60467dd2e5f68fd6ad988a4584430f) by Gunther Klessinger).
- Skips, transfer of old eval results, allowing md change w/o re-eval ([2f14dea](https://github.com/AXGKl/docutools/commit/2f14dea6287a0245b2ae3e8a76b12a0682233751) by Gunther Klessinger).
- Skips, transfer of old eval runs, allowing change of .lp w/o eval ([e38d075](https://github.com/AXGKl/docutools/commit/e38d075912b565704f1d2b94990f69a94bd0f8cf) by Gunther Klessinger).
- Lock_page header argument ([7f72159](https://github.com/AXGKl/docutools/commit/7f7215947f783b1c2bd2521160112ffcf2e66898) by Gunther Klessinger).
- Skips ([85abb23](https://github.com/AXGKl/docutools/commit/85abb232eaae2bded3c4bdb9349885f50132de5e) by Gunther Klessinger).


## [2021.8.3](https://github.com/AXGKl/docutools/releases/tag/2021.8.3)
<small>[Compare with 2021.8.2](https://github.com/AXGKl/docutools/compare/2021.8.2...2021.8.3)</small>

### Bug Fixes
- Sending hex to tmux ([2091804](https://github.com/AXGKl/docutools/commit/2091804a647ae454cc4cc36520c098b60491fdfc) by Gunther Klessinger).

### Features
- Source code block output ([2983917](https://github.com/AXGKl/docutools/commit/29839171becf4f48f696bf5a9c2881a319ac1880) by Gunther Klessinger).


## [2021.8.2](https://github.com/AXGKl/docutools/releases/tag/2021.8.2)
<small>[Compare with 2021.7.31](https://github.com/AXGKl/docutools/compare/2021.7.31...2021.8.2)</small>

### Bug Fixes
- Dt vars now also in tmux, as promised ([540d33b](https://github.com/AXGKl/docutools/commit/540d33b1ceb4e12bb59c42f9995b837397d1a612) by Gunther Klessinger).

### Features
- Multiline handling much smarter, with '> ' indicator line starts ([e8d60f9](https://github.com/AXGKl/docutools/commit/e8d60f9f825ddff8232abcd5916384db5ffb181f) by Gunther Klessinger).
- Better error msg on failing cwd ([8c7382a](https://github.com/AXGKl/docutools/commit/8c7382a36cf5126cfec3ef1ac0560647def38121) by Gunther Klessinger).
- Dt_... environ vars in all lit prog exec envs ([966c323](https://github.com/AXGKl/docutools/commit/966c323aa751d1de1b03e9231050306f2492b37c) by Gunther Klessinger).


## [2021.7.31](https://github.com/AXGKl/docutools/releases/tag/2021.7.31)
<small>[Compare with 2021.7.30](https://github.com/AXGKl/docutools/compare/2021.7.30...2021.7.31)</small>

### Features
- Pycond based assertion matching ([2a185ec](https://github.com/AXGKl/docutools/commit/2a185ecbf423b1603f92947b17287b3066fa64ba) by Gunther Klessinger).


## [2021.7.30](https://github.com/AXGKl/docutools/releases/tag/2021.7.30)
<small>[Compare with 2021.7.29](https://github.com/AXGKl/docutools/compare/2021.7.29...2021.7.30)</small>

### Features
- Better assertions, also lists and also for any mode, not only sessions ([6610a7a](https://github.com/AXGKl/docutools/commit/6610a7ac32166d4087b6355af68b4939a18941d5) by Gunther Klessinger).
- Assert and asserts on all lp modes ([ed7b449](https://github.com/AXGKl/docutools/commit/ed7b449935db8d880fc3af0551b4d024ee385fb8) by Gunther Klessinger).


## [2021.7.29](https://github.com/AXGKl/docutools/releases/tag/2021.7.29)
<small>[Compare with 2021.7.28](https://github.com/AXGKl/docutools/compare/2021.7.28...2021.7.29)</small>

### Bug Fixes
- Erradicating changlog rendering problems when using macros plugin ([c4cb379](https://github.com/AXGKl/docutools/commit/c4cb37987b0992d640c41f8679cc505dc182af65) by Gunther Klessinger).

### Features
- Xterm.css ([735a6dd](https://github.com/AXGKl/docutools/commit/735a6dd320d889e8373bb4f7c020cb93e02ef7bf) by Gunther Klessinger).


## [2021.7.28](https://github.com/AXGKl/docutools/releases/tag/2021.7.28)
<small>[Compare with 2021.7.27](https://github.com/AXGKl/docutools/compare/2021.7.27...2021.7.28)</small>

### Features
- Mkdocs makros ([f4b63f4](https://github.com/AXGKl/docutools/commit/f4b63f45862a50ca9459239140b66e2f45da9ce9) by Gunther Klessinger).


## [2021.7.27](https://github.com/AXGKl/docutools/releases/tag/2021.7.27)
<small>[Compare with 2021.5.14](https://github.com/AXGKl/docutools/compare/2021.5.14...2021.7.27)</small>

### Features
- Lcd feature ([0803f03](https://github.com/AXGKl/docutools/commit/0803f03b8ba71f47e405be9160a0406cf9901793) by Gunther Klessinger).


## [2021.5.14](https://github.com/AXGKl/docutools/releases/tag/2021.5.14)
<small>[Compare with 2021.5.13](https://github.com/AXGKl/docutools/compare/2021.5.13...2021.5.14)</small>


## [2021.5.13](https://github.com/AXGKl/docutools/releases/tag/2021.5.13)
<small>[Compare with 2021.5.12](https://github.com/AXGKl/docutools/compare/2021.5.12...2021.5.13)</small>


## [2021.5.12](https://github.com/AXGKl/docutools/releases/tag/2021.5.12)
<small>[Compare with 2021.5.11](https://github.com/AXGKl/docutools/compare/2021.5.11...2021.5.12)</small>


## [2021.5.11](https://github.com/AXGKl/docutools/releases/tag/2021.5.11)
<small>[Compare with first commit](https://github.com/AXGKl/docutools/compare/73480690fe3d737f5c5420547ead7279e52e5431...2021.5.11)</small>

