# /etc/profile.d/lang.sh - set i18n stuff

sourced=
for f in "$HOME/.i18n" /etc/sysconfig/i18n; do
	if [ -s "$f" ] && . "$f"; then
		sourced=1
		break
	fi
done

unset f

Unset()
{
	unset "$@" ||:
}

CondSet()
{
	local n
	for n in "$@"; do
		[ -n "$(eval "echo \"\$$n\"")" ] && export "$n" || Unset "$n"
	done
}

if [ -n "$sourced" ]; then
	CondSet LANGUAGE LC_ADDRESS LC_COLLATE LC_CTYPE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE LC_TIME
	[ -n "$LANG" ] && export LANG || Unset LANG
	if [ -n "$LC_ALL" ]; then
		[ "$LC_ALL" != "$LANG" ] && export LC_ALL || Unset LC_ALL
	else
		Unset LC_ALL
	fi
	if [ -n "$LINGUAS" ]; then
		[ "$LINGUAS" != "$LANG" -a "$LINGUAS" != "$LANGUAGE" ] && export LINGUAS || Unset LINGUAS
	else 
		Unset LINGUAS
	fi

	[ -n "$ENC" ] && export ENC || Unset ENC
	[ -n "$XIM" ] && export XIM || Unset XIM
	[ -n "$XIM_PROGRAM" ] && export XIM_PROGRAM || Unset XIM_PROGRAM
	[ -n "$XMODIFIERS" ] && export XMODIFIERS || Unset XMODIFIERS
	[ -n "$_XKB_CHARSET" ] && export _XKB_CHARSET || Unset _XKB_CHARSET

	if [ -n "$SYSFONTACM" ]; then
		case $SYSFONTACM in
			iso01*|iso02*|iso08*|iso15*|koi*|latin2-ucw*|cp1251*|pt154*)
				if [ "$TERM" = linux -a "`/sbin/consoletype`" = vt ]; then
					echo -ne '\033(K' >&0
				fi
				;;
		esac
	fi

	Unset SYSFONTACM SYSFONT

	# handling of special cases where localization is done
	# only on console or only on X11.
	if [ -n "$DISPLAY" ]; then
		if [ "$X11_NOT_LOCALIZED" = yes ]; then LANGUAGE=C; fi
	else
		if [ "$CONSOLE_NOT_LOCALIZED" = yes ]; then LANGUAGE=C; fi
	fi
	if [ -n "$LANGUAGE" ]; then export LANGUAGE; fi
fi

unset sourced
unset -f Unset CondSet
