---
layout: post
title:  "Disable a keyboard key in Ubuntu"
categories: ubuntu
---

To disable *Caps lock* , open a terminal, and run `xev -event keyboard`. It will open a app and if you press a key, the value will show on the screen. Then run the command below:

```bash
xmodmap -e “keycode <value> = "
```

On my machine, to disable *ctrl* should run:

```bash
xmodmap -e “keycode 37 = "
```

And then, the *Caps lock* is disable.