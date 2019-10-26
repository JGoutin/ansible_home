# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi

# Kodi startup
if [ -z "$DISPLAY" ] && [ "${XDG_VTNR:-0}" -eq 1 ]; then
        exec /usr/bin/xinit &>.xinit.log -- /usr/bin/X -s 0 -noreset -keeptty -nocursor -allowMouseOpenFail vt$XDG_VTNR
fi
