# /etc/profile.d/lang.sh - set i18n stuff

unset I18N_CFG_FILE

if [ -f $HOME/.i18n ]; then
    I18N_CFG_FILE=$HOME/.i18n
elif [ -f /etc/sysconfig/i18n ]; then
    I18N_CFG_FILE=/etc/sysconfig/i18n
fi

if [ -f "$I18N_CFG_FILE" ]; then
    . $I18N_CFG_FILE
    if [ -n "$LANG" ] ; then
       [ "$LANG" = "C" ] && LANG="en_US"
       export LANG
    else
       unset LANG
    fi
    [ -n "$LC_CTYPE" ] && export LC_CTYPE || unset LC_CTYPE
    [ -n "$LC_COLLATE" ] && export LC_COLLATE || unset LC_COLLATE
    [ -n "$LC_MESSAGES" ] && export LC_MESSAGES || unset LC_MESSAGES
    [ -n "$LC_NUMERIC" ] && export LC_NUMERIC || unset LC_NUMERIC
    [ -n "$LC_MONETARY" ] && export LC_MONETARY || unset LC_MONETARY
    [ -n "$LC_TIME" ] && export LC_TIME || unset LC_TIME
    if [ -n "$LC_ALL" ]; then
       if [ "$LC_ALL" != "$LANG" ]; then
         [ "$LC_ALL" = "C" ] && LC_ALL="en_US"
         export LC_ALL
       else
         unset LC_ALL
       fi
    else
       unset LC_ALL
    fi
    [ -n "$LANGUAGE" ] && export LANGUAGE || unset LANGUAGE
    if [ -n "$LINGUAS" ]; then
       if [ "$LINGUAS" != "$LANG" -a "$LINGUAS" != "$LANGUAGE" ]; then
          export LINGUAS
       else
          unset LINGUAS
       fi
    else 
       unset LINGUAS
    fi

    # some ugly back compatibility... should be removed in the future
    if [ ! -n "$RPM_INSTALL_LANG" ]; then
       if [ -n "$LANGUAGE" ]; then
          if [ -n "$LINGUAS" ]; then
              RPM_INSTALL_LANG=$LANGUAGE:$LINGUAS
          else
              RPM_INSTALL_LANG=$LANGUAGE
          fi
       else
          if [ -n "$LINGUAS" ]; then
              RPM_INSTALL_LANG=$LINGUAS
          else
              unset RPM_INSTALL_LANG
          fi
       fi
    fi

    if [ -n "$RPM_INSTALL_LANG" ]; then
       export RPM_INSTALL_LANG
    else
       unset RPM_INSTALL_LANG
    fi
    [ -n "$ENC" ] && export ENC || unset ENC
    [ -n "$XIM" ] && export XIM || unset XIM
    [ -n "$XMODIFIERS" ] && export XMODIFIERS || unset XMODIFIERS
    [ -n "$_XKB_CHARSET" ] && export _XKB_CHARSET || unset _XKB_CHARSET

    if [ -n "$SYSFONTACM" ]; then
	case $SYSFONTACM in
	    iso01*|iso02*|iso15*|koi*|latin2-ucw*)
		if [ "$TERM" = "linux" ]; then
		    if ls -l /proc/$$/fd/0 2>/dev/null | grep -- '-> /dev/tty[0-9]*$' >/dev/null 2>&1; then
			echo -n -e '\033(K' > /proc/$$/fd/0
		    fi
		fi
		;;
	esac
    fi

    unset SYSFONTACM
fi
