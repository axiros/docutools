# Darkmode

Pages are rendered based on your browser's preference, regarding dark mode:

![](img/darkmode.png){: : .zoom}
 
--8<--
zoom
--8<--





----


## How

Through a media query we adapt the colorscheme to the preferred one of the browser:

```html

 
    <body dir="ltr" data-md-color-scheme="preference" data-md-color-primary="yellow" data-md-color-accent="deep-purple">
      
        <script>matchMedia("(prefers-color-scheme: dark)").matches&&document.body.setAttribute("data-md-color-scheme","slate")</script>
      

```

!!! hint "Linux/Chromium"

    On Linux do this for chromium, should it not respect your system prefs: 

    ```
    ~/.config ❯ cat chromium-flags.conf
    --force-dark-mode
    --enable-features=WebUIDarkMode
    ```



