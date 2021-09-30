# Stats :srcref:fn=src/lcdoc/mkdocs/stats/__init__.py,t=

Usage: :srcref:fn=src/lcdoc/assets/mkdocs/mkdocs.yml,m=lcd-stats,t=m

- Writes collected stats to a file or stdout after build, intended for consolidation e.g. with [jq](https://stedolan.github.io/jq/download/)
- Presents deviations
- Runs a post build simple consolidation of major log events, presents them and triggers a build
  break at presence of log with severity higher than a configurable value

    !!! important 
        You **have** to enable this plugin, when you want LP build breaks on CI based on lcd plugin log
        errors or higher severity.



## Mechanics

- All hooks of plugins inheriting from `lcdoc.mkdocs.MDPlugin` are wrapped into a decorator, which
    - sets a named stats dict into them, so they can just set counters and metrics into those dicts.
    - customizes their logging
- When the hooks are page hooks we set the stats dicts per page.


## Config


`lp:show_src delim=stats_config dir=src/lcdoc`

## Stats Output

On config setting `dump_stats`, we will dump all stats to the configured file

### Example Output

```bash lp fmt=mk_console 
cat $LP_PROJECT_ROOT/build/lcd-stats.json| head -n 20 || true # on CI the first run will have no such file
```

### Diff Output

We keep the stats from the last run and compare at every build, logging the diff.

=== "Example: Post build output diff after adding an LP block"

    ```js
    INFO     -  Stats changes since last run   [StatsPlugin]
    {
        "added": {
            "Pages.LPPlugin.on_page_markdown.features/mypage/My Page.blocks_evaled": 1,
            "Pages.LPPlugin.on_page_markdown.features/mypage/My Page.blocks_total": 1
        },
        "changed": {
            "Log.debug": [
                144,
                145
            ],
            "Log.info": [
                8,
                9
            ]
        }
    }
    ```

## Logging

### `$ignore_err`

- `mkdocs build` will fail at error levels including and above `error`.
- You can lower error logs by setting `$ignore_err`, matching the log message to be lowered from
  `error` (or higher) to just `warning`.

Example: In ci.yml:

```yaml
env:
    ignore_err: "No coverage files"
```

### Log Dumps

On config setting `dump_logs`, we will dump all created logs in line-sep json form to the given file
(backing up the previous one)

!!! tip

    The output of debug level logging is often overwhelming and inter build changes are hard to see, but
    you'll see a change of log statement counts in the diff.

    If you are interested in *why* log counts changed you can diff the previous logs output with
    the current one.

!!! warning
    
    Some "expensive" debug logs are not even sent to the logging system, when level is info or
    higher. Those logs cannot occur in the log dumps then. In order to get really all possible debug
    logs, you have to run mkdocs with `-v`.


### Example Output

```bash lp fmt=mk_console 
cat $LP_PROJECT_ROOT/build/lcd-logs.json| head -n 20 || true # on CI the first run will have no such file
```




