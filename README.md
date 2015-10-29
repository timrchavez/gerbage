Gerbage
-------

Gerbage is a project that lets you relay Gerrit events into IRC channels.
It is intended to be used with a private IRC server because it uses IRC as
an interface and people would probably be annoyed and / or confused if you
tried using this on a public network.

So is Gerbage a bot?  Actually it's worse than that.  It's a Gerrit event
listener that spawns many bots.  Gerrit projects because their own IRC
channels.  So Gerrit events for 'openstack/nova' will be relayed to
'#openstack/nova'.  The nick of the bot that relays the event will be the
Gerrit username of the uploader, approver, etc.  Depending on the IRC server
you're running you can take this IRC-as-your-UI abstraction a bit further.
For example, if you don't want to receive Gerrit event notifications for a
particular person in a project (why you'd want to do this, I do not know..)
you can /mode +q them.  You'll also have a nice log of Gerrit events in your
IRC logs separated by channel/project which should give you a nice summary
of the day or give you a way to quickly grep changes.

Anyway.

How To Run
----------

 * ./setup.sh
 * source venv/bin/activate
 * Edit code to point at IRC server (see Todo)
 * ./start.sh

Supported Events
----------------

 * patchset-created
 * change-merged

Todo
----

 * Add a config file mechanism to load stuff like server settings form disk
 * Add support for more Gerrit events

Notes on IRC Server
-------------------

I run a private IRC server (on localhost) co-located with my ZNC bouncer and
connect to it that way.  It works our pretty well for now.  You should try it.
