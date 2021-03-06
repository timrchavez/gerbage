Gerbage
-------

Gerbage is a project that lets you relay Gerrit events into IRC channels.
It is intended to be used with a private IRC server because it uses IRC as
an interface and people would probably be annoyed and / or confused if you
tried using this on a public network.

So is Gerbage a bot?  Actually it's worse than that.  It's a Gerrit event
listener that spawns many bots.  Gerrit projects become their own IRC
channels and Gerrit submitters, approvers, etc become IRC users that
tell you when they do things in Gerrit.

So.  As an illustration Gerrit events for 'openstack/nova' will be relayed to
the '#openstack/nova' IRC channel and the nick of the bot that relays an event
will be the Gerrit username of the uploader, approver, etc of that event.  And
it gets better!  Depending on the IRC server you're running, you can take this
abstraction a bit further.

For example, if you don't want to receive Gerrit event notifications for a
particular person in a project (why you'd want to do this, I do not know, but
maybe you do) you can /mode +q them to silence those events.  Also in addition
to getting greppable logs (which you'd get anyway with a bot siting on one
channel relaying events for all projects), I find you're getting a nice,
digestable summary of activity since there is no conversation happening
in the project channels.  You're also in control of what data gets relayed.
That's nice too!

Anyway.  This is still a pretty bad idea, but my trial run of it is working
out nicely.

How To Run
----------

 * sudo apt-get install virtualenv python-dev build-essential
 * source venv/bin/activate
 * Edit gerbage/settings.py to post at IRC server
 * Edit gerbage/zoidberg/conf.yaml to point at your Gerrit SSH key, etc
 * ./setup.sh
 * ./start.sh

Supported Events
----------------

 * patchset-created
 * change-merged

Todo
----

 * Add support for more Gerrit events

Notes on IRC Server
-------------------

I run a private IRC server (on localhost) co-located with my ZNC bouncer and
connect to it that way.  It works our pretty well for now.  You should try it.
