#!perl

use warnings;
use strict;

use POE::Kernel;
use POE::Session;

POE::Session->create(
	inline_states => {
		_start => sub {
			print "hello, world!\n";
			$_[KERNEL]->post($_[SESSION], "loop", 1 );
		},
		loop   => sub {
			my $iterator = $_[ARG0];
			print "$iterator\n";
			$_[KERNEL]->yield( loop => ++$iterator ) if $iterator < 5;
		},
		_stop  => sub { print "bye now.\n" },
	}
);

print "starting the main loop...\n";
POE::Kernel->run();
print "main loop stopped.\n";
exit;

__END__

Output:

hello, world!
starting the main loop...
1
2
3
4
5
bye now.
main loop stopped.

Notes:

Event information is passed to handlers in @_.  Members of @_ are
identified by their position within that array.  POE::Session defines
constants for each position within @_ so that you don't need to rely
on magic numbers to extract individual members.  For example the
KERNELth member ($_[KERNEL]) contains the program's POE::Kernel
object.  $_[SESSION] is the currently active session (the one that the
event is being handled within).  $_[HEAP] is that session's data
context, and so on.

Events have a lot of data members, so it's impractical to assign them
the usual way.  my ($kernel, heap) = @_; is impractical, and passing
events as hash references tends to be slower than using @_ as it was
intended.

These @_ offset constants are used almost all the time, so
POE::Session exports them automatically.  This is convenient, but it
causes a lot of people to wonder where the constants come from.

Sessions may post their own events in addition to watching for events
from the real world.  The post() method simply sends an event to some
session with some optional parameters.

Posting events within the currently active session is such a common
operation that yield() was created.  yield() is syntactic sugar for
post($_[SESSION], ...).  When considered as an alias for post(), it
becomes apparent that yield() does not interrupt execution of the
current event handler.  People accustomed to threads or generators
would expect different of yield().

Events may contain their own state information, as they do here.  When
using events to maintain run state, it's important to pass the run
state along with associated events.

Sessions run as long as they have events in play or watchers to create
new events.  The "loop" event handler stops the session by declining
to put another event in play.  There are other, more obscure
conditions in which a session remains alive, but they will be covered
in depth later.
