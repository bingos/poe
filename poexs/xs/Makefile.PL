
use ExtUtils::MakeMaker;

WriteMakefile(
	NAME => 'POE::XS',
	VERSION_FROM => '../lib/POE/XS.pm',
	OBJECT => q/$(O_FILES)/, # pick up all the xs files
	depend => {
		'$(FIRST_MAKEFILE)' => '$(VERSION_FROM)',
	}, # this forces the Makefile to be rebuilt when our version changes
);
