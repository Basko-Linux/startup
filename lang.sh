# /etc/profile.d/lang.sh - set i18n stuff

Unset()
{
	unset "$@" ||:
}

sourced=
for f in "$HOME/.i18n" /etc/sysconfig/i18n; do
	if [ -f "$f" ] && . "$f"; then
		sourced=1
		break
	fi
done

Unset f

if [ -n "sourced" ]; then
	if [ -n "$LANG" ]; then
		if [ "$LANG" = "C" ]; then LANG="en_US"; fi
		export LANG
	else
		Unset LANG
	fi
	[ -n "$LC_CTYPE" ] && export LC_CTYPE || Unset LC_CTYPE
	[ -n "$LC_COLLATE" ] && export LC_COLLATE || Unset LC_COLLATE
	[ -n "$LC_MESSAGES" ] && export LC_MESSAGES || Unset LC_MESSAGES
	[ -n "$LC_NUMERIC" ] && export LC_NUMERIC || Unset LC_NUMERIC
	[ -n "$LC_MONETARY" ] && export LC_MONETARY || Unset LC_MONETARY
	[ -n "$LC_TIME" ] && export LC_TIME || Unset LC_TIME
	if [ -n "$LC_ALL" ]; then
		if [ "$LC_ALL" != "$LANG" ]; then
			if [ "$LC_ALL" = "C" ]; then LC_ALL="en_US"; fi
			export LC_ALL
		else
			Unset LC_ALL
		fi
	else
		Unset LC_ALL
	fi
	[ -n "$LANGUAGE" ] && export LANGUAGE || Unset LANGUAGE
	if [ -n "$LINGUAS" ]; then
		if [ "$LINGUAS" != "$LANG" -a "$LINGUAS" != "$LANGUAGE" ]; then
			export LINGUAS
		else
			Unset LINGUAS
		fi
	else 
		Unset LINGUAS
	fi

	# some ugly back compatibility... should be removed in the future
	if [ -z "$RPM_INSTALL_LANG" ]; then
		if [ -n "$LANGUAGE" ]; then
			if [ -n "$LINGUAS" ]; then
				RPM_INSTALL_LANG="$LANGUAGE:$LINGUAS"
			else
				RPM_INSTALL_LANG="$LANGUAGE"
			fi
		else
			if [ -n "$LINGUAS" ]; then
				RPM_INSTALL_LANG="$LINGUAS"
			else
				Unset RPM_INSTALL_LANG
			fi
		fi
	fi

	if [ -n "$RPM_INSTALL_LANG" ]; then
		export RPM_INSTALL_LANG
	else
		Unset RPM_INSTALL_LANG
	fi

	[ -n "$ENC" ] && export ENC || Unset ENC
	[ -n "$XIM" ] && export XIM || Unset XIM
    [ -n "$XIM_PROGRAM" ] && export XIM_PROGRAM || Unset XIM_PROGRAM
	[ -n "$XMODIFIERS" ] && export XMODIFIERS || Unset XMODIFIERS
	[ -n "$_XKB_CHARSET" ] && export _XKB_CHARSET || Unset _XKB_CHARSET

	if [ -n "$SYSFONTACM" ]; then
		case $SYSFONTACM in
			iso01*|iso02*|iso15*|koi*|latin2-ucw*|cp1251*)
				if [ "$TERM" = "linux" ] && /bin/ls -l /proc/self/fd/0 2>/dev/null |grep -qs -- '-> /dev/tty[0-9]*$'; then
					echo -ne '\033(K' >/proc/self/fd/0
				fi
				;;
		esac
	fi

	Unset SYSFONTACM SYSFONT

	# handling of special cases where localization is done
	# only on console or only on X11.
	if [ -n "$DISPLAY" ]; then
		if [ "$X11_NOT_LOCALIZED" = "yes" ]; then LANGUAGE=C; fi
	else
		if [ "$CONSOLE_NOT_LOCALIZED" = "yes" ]; then LANGUAGE=C; fi
	fi
	if [ -n "$LANGUAGE" ]; then export LANGUAGE; fi
fi

Unset sourced
unset -f Unset
