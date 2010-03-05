#!perl

use warnings;
use strict;

use POE::Kernel;
use POE::Session;

POE::Session->create(
	inline_states => {
		_start  => sub { print "hello, world!\n" },
		_stop   => sub { print "bye now.\n" },
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
bye now.
main loop stopped.

Notes:

Every POE program must have a single POE::Kernel object.  This is such
an immutable rule that POE::Kernel creates one for you when it's
loaded.

Every POE program must have one or more POE::Session objects if it
will be expected to run.  POE::Session objects act as tasks or
"sessions" within a program.  POE::Kernel->run() executes for as long
as there are sessions to drive.  That is, run() returns after the last
session has handled its _stop event.

POE::Kernel manages sessions and event watchers.  When events occur,
it calls predefined code belonging to the appropriate POE::Session
objects.

Because a session's code will only execute during the course of
handling, it can be said to be "event driven".

Actions taken while a session is handling an event is said to happen
"inside" that session.  For example, the print() statements in the
_start and _stop handlers are executed inside that session.
Conversely, the print() statements around POE::Kernel->run() are
executed outside the session.

Event handlers are known as "states" for a legacy reason: POE sessions
were originally designed to be event-driven state machines for a
higher level language.  They may still be used as such, but most
people don't do this.  So "state" and "event handler" are often
interchangeable in POEspeak.

Sessions have data contexts as well as execution contexts.  A
session's "heap" is some session-scoped data that is always available
within a session.  It's not so easily available outside the session.

Every event is the combination of a few contexts: The POE::Kernel
object's context, the context of the POE::Session that will be
handling the event, potential POE-provided context for the event, and
user-supplied event context.  The previously mentioned "heap" is part
of the session's context.  The name of the event is an example of some
event context.  And so on.

Sessions are not created with new().  They once were, but new()'s
syntax was lame and had to be deprecated.  new() will return as an
alias for create() after a suitable amount of downtime.

Sessions are created, but their objects are not saved anywhere.
POE::Kernel manages sessions by holding onto them as long as they're
needed.  It releases them when they're done, letting Perl garbage
collect them if you don't have a reference to them.

Some events, such as _start and _stop, are provided by POE.  They have
standard names, always beginning with an underscore.

A _start event handler is required.  Session startup has been
standardized so POE::Kernel always knows how to initialize them.

The _start handler is called as part of create().  Sessions are "done"
when they have run out of events to handle, and nothing exists in the
program that might send them more events.  Sending a _start event
synchronously as part of create() allows the session to set up its
task before POE::Kernel has a chance to test it for "doneness".

Synchronous _start is also necessary for _child and _parent events,
which are described elsewhere.

Handling _stop is optional.  The _stop event is advisory---it
indicates that the session is in the throes of destruction.  You can't
do much from _stop since any and all lingering things owned by the
session will be destroyed once the handler returns.
