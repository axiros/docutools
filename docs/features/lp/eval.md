# Evaluation and Caching

!!! note
    Understanding and controlling when blocks are evaluated is important for the **author** of docsets, (not the reader.

## Best Practice

These are the recommended base settings to control evaluation:

- Before mkdocs build: `export lp_eval=always`
- Before mkdocs serve: `export lp_eval=on_page_change`

They are also set by the :srcref:make:on_page_change file.

Within the page header you might want to set `eval` page wide to `on_page_change`, in order to
prevent CI/CD to re-evaluate the page and commit the `.res.py` file for those pages.


Here the Details:

## Hashing

When the plugin identifies and parses lp blocks within your docset, it builds a hash to identify
them.

The hash is built over the complete lp body plus a specific set of header parameters, which might,
when changed, result in a different outcome of the evaluation:

```python lp mode=show_src delim=hashed_headers dir=src/lcdoc eval=always
```

!!! warning
    It should be clear that the evaluation result might change, even *without* any change in those
    headers, due to side-effects outside of our control. It remains upone the author of LP stanzas
    to decide upon re-evaluation. 


## Cache Files

After a page was evaluated, a file is written, next to the `.md` source file, ending with `.res.py`.
The file contains a hash map, with keys the hashes of each block and value the raw (unformatted) result of the evaluation.

The `eval` parameter determines now, if, at page build time, a new evaluation is performed or the
result from the cache is taken, if available.

### Patching the mkdocs file watcher

At first start of mkdocs <build|serve> we have to patch the filewatcher of mkdocs, in order to
ignore `.res.py` files. That prevents putting them into the site directory but also helps avoid
evaluation loops.

```python lp mode=show_src delim=patching_mkdocs dir=src/lcdoc hide=implementation eval=always

```





### CI/CD: Comitting Cache Files?

Sometimes lp blocks can or should only be evaluated on your local machine - but not on CI/CD elsewhere.

Example: You document how to set up a Kubernetes cluster in the cloud, using your cloud provider
credentials, plus it takes 30 minutes until completed.

> You want to be able to prevent CI/CD to evaluate the specific blocks - or whole pages -, when running, i.e. when CI/CD is building the docs.

Solution: Set `eval` to "on_change" or "on_page_change" 

- You commit the `.res.py` cache files of these pages and
- set `eval` to "on_change" or "on_page_change".
- The result (cache) files, for pages which should be evaluated on CI/CD (e.g. for additional testing purposes) you do NOT
  commit. 
- Then the final docs will display the result from your local run, for the pages you committed the
  cache files for.



## The `eval` Parameter

Adjusting `eval` is key for having fast edit-render cycles, while authoring pages.

### Predefined Values
```python lp mode=show_src delim=eval_parameter_values dir=src/lcdoc eval=always
```

- never: No evaluation. Typically given on page level, while writing a bunch of LP statements. Will never eval, even with a cache miss.
- on_change: Re-evaluation when the hash changes
- on_page_change: Re-evaluation of all blocks, when *any* hash changes on the page
- always: Always evaluate (the default)

### Arbitrary Matching

When working on a block or a page, you can also restrict evaluation to the current page or even
block only, by specifying the `eval` parameter like so: `<page match>[:<block match>]`.

Typically you do this via an environ parameter at start up of `mkdocs build|serve`:

!!! warning
    Such a page match is checked against the full source path to markdown pages, from `/` (root) folder!
    So `lp_eval=docs/index` would match exactly on your main index.md.

```console
$ lp_eval="mypage" mkdocs build
$ lp_eval="mypage:myblockmatch" mkdocs build
```

When a block match was given, you can just add the match string within the header, e.g. as a
boolean value. 

Example:
```
 ```bash lp myblockmatch
 < statements to eval>
 ```
```

When the block is correctly functioning, you can delete the match string and have the result in the
cache file, moving on to the next block.

Any non matching block is set to `eval="never"`, i.e. results will be from cache - or when not
present rendered as skipped.

!!! hint
    To cause more than one block evaluated simply add the matching keyword argument in the header for all blocks you want.



## Skips

The header exclusive argument `<lang> lp skip_<this|other|below|above>` will skip block execution
accordingly, i.e. you can work your way towards a completely evaluatable page, from block to block. 


!!! note
    Behind the scenes, the `eval` parameter does nothing else than adding `skip_this` parameters to
    non evaluated blocks.








