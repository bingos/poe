
#include "EXTERN.h"
#include "perl.h"
#include "XSUB.h"

MODULE = POE::XS    PACKAGE = POE::XS

BOOT:
	// boot other xs files using a modified version of the comment below
	// boot POE__Kernel(aTHX_ cv);

MODULE = POE::XS    PACKAGE = POE::XS    PREFIX = poe_xs_


