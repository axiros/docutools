# Sessions

Some plugins, currently [bash][bash] and [python][python] support sessions, via which you can
transfer state between LP blocks. 

See the specific plugins for technical details.

Here we only explain the differences.

## The Multipurpose [Shell Session](../bash/sessions.md)

- Spawns a tmux process, sends commands in, read results out.
- Can be used not only for code but e.g. also to control REPLs:

### Example Node Session

Typically this would be [`silent`](../parameters.md#silent)

```javascript lp new_session=nodejs_test addsrc="Starting nodejs" expect=> fmt=xt_flat
node
```

Now you have a node session and can do things - but first keep params at one place:

```page lp session=nodejs_test addsrc prompt=> expect=> fmt=xt_flat
```

First interaction:

```javascript lp
answer = 42
```


Second  interaction:

```javascript lp
console.log('The answer to everything is:', answer)
```

!!! note

    - As you can see the coloring is from nodejs, not from the javascript html pretty print. We have
      javascript as language only for syntax highlighting within the editor.
    - The LP sources are shown only due to the [`addsrc`](../parameters.md#addsrc) parameter in our
      block headers.



## The Python Session

While tmux sessions are run within a subprocess, python session state is resident within the mkdocs
build process itself - no need to send and read strings via the tmux api here (mkdocs *is* a python
process).





[bash]: ../bash/sessions.md
[python]: ../python/


