# /etc/profile.d/lang.csh - set i18n stuff

set sourced=0

foreach file ($HOME/.i18n /etc/sysconfig/i18n)
	if ($sourced == 0 && -f $file ) then
	    eval `sed 's|=C$|=en_US|g' $file | sed 's|^#.*||' | sed 's|\([^=]*\)=\([^=]*\)|setenv \1 \2|g' | sed 's|$|;|' `
	set sourced=1
	endif
end

if ($sourced == 1) then
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
	    case iso01*:
	    case iso02*:
	    case iso15*:
	    case koi*:
	    case latin2-ucw*:
	    case cp1251*:
	    case pt154*:
	        if ( $?TERM ) then
		    if ( "$TERM" == "linux" ) then
		        if ( `/sbin/consoletype` == "vt" ) then
			    /bin/echo -n -e '\033(K' > /dev/stdin
		        endif
		    endif
		endif
		breaksw
	endsw
    endif
    unsetenv SYSFONTACM
    unsetenv SYSFONT
endif
