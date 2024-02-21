Sandbox Mode
============

Sandbox mode allows administrator users to experiment with plugins and themes, by allowing 
write access to the relevant directories.
It is enabled by setting [SANDBOX_MODE][].

> **Warning:**
> Use at your own risk; sandbox mode is experimental and there are a number of gotchas, both 
> known and unknown.


Gotchas
-------

### Ephemeral Extensions

*Anything installed through the admin interface is not retained across restarts, even if the 
volumes used are.*

You should take note of the packages installed and add them to site settings as soon as you 
have determined they are *probably* suitable.

### Untidy and Possibly Insecure

*Potentially everything is available to anyone who can access a site*

Sandbox mode works by moving the installable extensions directories (plugins, themes, 
language-packs) to the volume shared with the Nginx frontend.  This is necessary to make any 
static content that is installed after startup available to the frontend.

This approach puts *all* the extension content where it can be served by the frontend,
effectively bypassing the filtering of [STATIC_PATTERNS][]) for the plugin, theme and 
language-pack directories.  Unexpected content may be served and it may also present 
a heightened security risk.


[SANDBOX_MODE]: configuration.md#sandbox_mode
[STATIC_PATTERNS]: configuration.md#static_patterns
