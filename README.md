## or-applet - A Gtk+ Tor System Tray applet
#### Yawning Angel (yawning at schwanenlied dot me)

### What?

This is a stem/pygobject based Tor controller.  It primarily exists so I can
get quick info out of the system Tor instance on my laptop, if it happens to be
useful for other people, that's great.

### Dependencies

 * [pygobject3](https://wiki.gnome.org/PyGObject)
 * [stem](https://stem.torproject.org/)

The versions used for development are pygobject 3.12 and stem 32b9f75, other
versions are not supported.  The "Stem Prompt" launcher requires urxvt and
stem/interpretor (not installed by default) to work, and modifications to the
code to fix readline brain damage with the colored prompt.

#### Why doesn't or-applet work on "Insert-random-OS-or-distribution-here"?

 * Because I don't use it.
 * No, I don't care.
 * No, I won't fix it unless you send me clean paches.

### TODO

 * Add more stuff that I find useful.

### MIGHT DO

 * Add support for password auth on the control port, even though I don't use
   it.

### WON'T DO

 * Anything involving the words "Windows", "Darwin", "CentOS" or "Debian"
   unless it's accompanied by "please merge this patch".  Like previously
   stated, this exists for use on my systems.
 * Anything involving the words "GeoIP".  I don't reduce my anonymity set by
   enaging in StrictExitNodes/ExitNodes tinfoil-hattery.

### Credits

 * Leek icon by Robin Weatherall (http://www.robinweatherall.eu)

