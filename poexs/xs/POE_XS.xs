
#include "EXTERN.h"
#include "perl.h"
#include "XSUB.h"

MODULE = POE::XS    PACKAGE = POE::XS

PROTOTYPES: ENABLE
VERSIONCHECK: ENABLE

BOOT:
	// boot other xs files using a modified version of the line below
	boot_POE__Kernel(aTHX_ cv);
	boot_POE__Session(aTHX_ cv);
	boot_POE__Queue(aTHX_ cv);

MODULE = POE::XS    PACKAGE = POE::XS    PREFIX = poe_xs_


