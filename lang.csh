# /etc/profile.d/lang.csh - set i18n stuff

unset I18N_CFG_FILE

test -f $HOME/.i18n
if ($status == 0) then
   set I18N_CFG_FILE = $HOME/.i18n
else
   test -f /etc/sysconfig/i18n
   if ($status == 0) then
      set I18N_CFG_FILE = /etc/sysconfig/i18n
   endif
endif

if ($?I18N_CFG_FILE) then
    eval `sed 's|=C$|=en_US|g' $I18N_CFG_FILE | sed 's|\([^=]*\)=\([^=]*\)|setenv \1 \2|g' | sed 's|$|;|' `
    if ($?LC_ALL && $?LANG) then
        if ($LC_ALL == $LANG) then
            unsetenv LC_ALL
        endif
    endif
    if ($?LINGUAS && $?LANG) then
        if ($LINGUAS == $LANG) then
            unsetenv LINGUAS
        endif
    endif
    if ($?LINGUAS && $?LANGUAGE) then
        if ($LINGUAS == $LANGUAGE) then
            unsetenv LINGUAS
        endif
    endif

    if ($?SYSFONTACM) then
        switch ($SYSFONTACM)
	    case iso01*|iso02*|iso15*|koi*|latin2-ucw*|cp1251*:
	        if ( $?TERM ) then
		    if ( "$TERM" == "linux" ) then
		        if ( ls -l /proc/$$/fd/0 2>/dev/null | grep -- '-> /dev/tty[0-9]*$' >/dev/null 2>&1)  then
			    echo -n -e '\033(K' > /proc/$$/fd/0
		        endif
		    endif
		endif
		breaksw
	endsw
    endif
    unsetenv SYSFONTACM
endif
