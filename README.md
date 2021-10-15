#  docutools

<!-- badges -->
[![docs pages][docs pages_img]][docs pages] [![gh-ci][gh-ci_img]][gh-ci] [![pkg][pkg_img]][pkg] [![code_style][code_style_img]][code_style] 

[docs pages]: https://axiros.github.io/docutools
[docs pages_img]: https://axiros.github.io/docutools/img/badge_docs.svg
[gh-ci]: https://github.com/axiros/docutools/actions/workflows/ci.yml
[gh-ci_img]: https://github.com/axiros/docutools/actions/workflows/ci.yml/badge.svg
[pkg]: https://pypi.org/project/docutools/2021.10.16/
[pkg_img]: https://axiros.github.io/docutools/img/badge_pypi.svg
[code_style]: https://pypi.org/project/axblack/
[code_style_img]: https://axiros.github.io/docutools/img/badge_axblack.svg
<!-- badges -->


## [MkDocs Documentation](https://axiros.github.io/docutools/) Tools For Developers

This repo is providing a set of plugins for [mkdocs material](https://squidfunk.github.io/mkdocs-material/) compatible documentation.

It is meant to be used as a development dependency for projects, intended to be used mainly by the
developers themselves, i.e. for the more technical, code centric parts of software project documentation.

Most notable feature: **[Literate Programming](https://axiros.github.io/docutools/features/lp/)**, i.e. dynamic code execution - tightly integrated within the mkdocs framework.


> Most plugins should work in [other](https://www.mkdocs.org/dev-guide/themes/) mkdocs themes as well. No guarantees though.



## [Feature](https://axiros.github.io/docutools/features/) Gallery

<!-- gallery --><table id=gallery>
<tr>
<td style="cursor: pointer" title="features/lp/bash" class="even" onclick="window.location.href='features/lp/bash'">
<a href="https://axiros.github.io/docutools/features/lp/bash/">bash</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/bash/img/gl_lp_any.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/bash" class="odd" onclick="window.location.href='features/lp/bash'">
<a href="https://axiros.github.io/docutools/features/lp/bash/">bash</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/bash/img/gl_lp_async.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/bash" class="even" onclick="window.location.href='features/lp/bash'">
<a href="https://axiros.github.io/docutools/features/lp/bash/">bash</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/bash/img/gl_lp_ctrl_c.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/python/call_flow_logging" class="odd" onclick="window.location.href='features/lp/python/call_flow_logging'">
<a href="https://axiros.github.io/docutools/features/lp/python/call_flow_logging/">call_flow_logging</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/call_flow_logging/img/gl_cfl.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/call_flow_logging" class="even" onclick="window.location.href='features/lp/python/call_flow_logging'">
<a href="https://axiros.github.io/docutools/features/lp/python/call_flow_logging/">call_flow_logging</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/call_flow_logging/img/gl_cfl_details.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/chart" class="odd" onclick="window.location.href='features/lp/plugs/chart'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/chart/">chart</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/chart/img/gl_chart.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/plugs/chartist" class="even" onclick="window.location.href='features/lp/plugs/chartist'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/chartist/">chartist</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/chartist/img/gl_chartist.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/column" class="odd" onclick="window.location.href='features/lp/plugs/column'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/column/">column</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/column/img/gl_columns.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/comments" class="even" onclick="window.location.href='features/lp/python/comments'">
<a href="https://axiros.github.io/docutools/features/lp/python/comments/">comments</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/comments/img/gl_comments.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/python/cov_report" class="odd" onclick="window.location.href='features/lp/python/cov_report'">
<a href="https://axiros.github.io/docutools/features/lp/python/cov_report/">cov_report</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/cov_report/img/gl_cov_backref.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/data_table" class="even" onclick="window.location.href='features/lp/python/data_table'">
<a href="https://axiros.github.io/docutools/features/lp/python/data_table/">data_table</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/data_table/img/gl_data_tables.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/diag_diagram" class="odd" onclick="window.location.href='features/lp/python/diag_diagram'">
<a href="https://axiros.github.io/docutools/features/lp/python/diag_diagram/">diag_diagram</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/diag_diagram/img/gl_diag.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/plugs/drawio" class="even" onclick="window.location.href='features/lp/plugs/drawio'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/drawio/">drawio</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/drawio/img/gl_drawio.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/find-pages" class="odd" onclick="window.location.href='features/find-pages'">
<a href="https://axiros.github.io/docutools/features/find-pages/">find-pages</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/find-pages/img/gl_find_pages.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/flowchart" class="even" onclick="window.location.href='features/lp/plugs/flowchart'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/flowchart/">flowchart</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/flowchart/img/gl_flow.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/python/git_changelog" class="odd" onclick="window.location.href='features/lp/python/git_changelog'">
<a href="https://axiros.github.io/docutools/features/lp/python/git_changelog/">git_changelog</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/git_changelog/img/gl_changel.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/kroki" class="even" onclick="window.location.href='features/lp/plugs/kroki'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/kroki/">kroki</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/kroki/img/gl_kroki.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/kroki" class="odd" onclick="window.location.href='features/lp/plugs/kroki'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/kroki/">kroki</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/kroki/img/gl_kroki_cheat.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/plugs/lightbox" class="even" onclick="window.location.href='features/lp/plugs/lightbox'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/lightbox/">lightbox</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/lightbox/img/gl_light.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/lprunner" class="odd" onclick="window.location.href='features/lp/python/lprunner'">
<a href="https://axiros.github.io/docutools/features/lp/python/lprunner/">lprunner</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/lprunner/img/gl_lprunner.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/make_badges" class="even" onclick="window.location.href='features/lp/plugs/make_badges'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/make_badges/">make_badges</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/make_badges/img/gl_badges.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/plugs/markmap" class="odd" onclick="window.location.href='features/lp/plugs/markmap'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/markmap/">markmap</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/markmap/img/gl_mark.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/md-replace" class="even" onclick="window.location.href='features/md-replace'">
<a href="https://axiros.github.io/docutools/features/md-replace/">md-replace</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/md-replace/img/gl_md_repl.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/plugs/mermaid" class="odd" onclick="window.location.href='features/lp/plugs/mermaid'">
<a href="https://axiros.github.io/docutools/features/lp/plugs/mermaid/">mermaid</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/plugs/mermaid/img/gl_merm.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/page-tree" class="even" onclick="window.location.href='features/page-tree'">
<a href="https://axiros.github.io/docutools/features/page-tree/">page-tree</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/page-tree/img/gl_tree_ex.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python/project_dependencies" class="odd" onclick="window.location.href='features/lp/python/project_dependencies'">
<a href="https://axiros.github.io/docutools/features/lp/python/project_dependencies/">project_dependencies</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/project_dependencies/img/gl_auto_deps.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/python" class="even" onclick="window.location.href='features/lp/python'">
<a href="https://axiros.github.io/docutools/features/lp/python/">python</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/img/gl_lp_html.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="features/lp/python/screenshot" class="odd" onclick="window.location.href='features/lp/python/screenshot'">
<a href="https://axiros.github.io/docutools/features/lp/python/screenshot/">screenshot</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/python/screenshot/img/gl_shots.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/stats" class="even" onclick="window.location.href='features/stats'">
<a href="https://axiros.github.io/docutools/features/stats/">stats</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/stats/img/gl_stats.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
<td style="cursor: pointer" title="features/lp/xterm" class="odd" onclick="window.location.href='features/lp/xterm'">
<a href="https://axiros.github.io/docutools/features/lp/xterm/">xterm</a><br/><img onclick="event.stopPropagation();" src="https://axiros.github.io/docutools/features/lp/img/gl__xterm.png" style="display: block; padding: 3%; margin: auto; max-height: 500px"></img>
</td>
</tr>
<tr>
<td style="cursor: pointer" title="" class="even" onclick="window.location.href=''">
</td>
<td style="cursor: pointer" title="" class="odd" onclick="window.location.href=''">
</td>
<td style="cursor: pointer" title="" class="even" onclick="window.location.href=''">
</td>
</tr>
</table><!-- gallery -->
Last modified: Tue, 28 Sep 2021 10h GMT 