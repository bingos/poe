
use ExtUtils::MakeMaker;

WriteMakefile(
	NAME => 'POE::XS',
	VERSION => qw($Revision$)[1],
	OBJECT => q/$(O_FILES)/, # pick up all the xs files
);
