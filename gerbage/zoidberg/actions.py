import gevent

from zoidberg import actions
from gerbage.bot import GerritBot
from gerbage.settings import IRC_HOST, IRC_PORT
from gevent import queue

from gevent import monkey; monkey.patch_all()


gerrit_event_queues = {}

@actions.ActionRegistry.register("gerbage.CapturePatchsetCreated")
class CapturePatchsetCreatedAction(actions.Action):
    def _do_run(self, event, cfg, action_cfg, source):
        global gerrit_event_queues
        change = event.change
        uploader = event.uploader
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if uploader.username in gerrit_event_queues:
            gerrit_event_queues[uploader.username].put(
                (channel, "patchset-created", event))
        else:
            gerrit_event_queues[uploader.username] = queue.Queue()
            gerrit_event_queues[uploader.username].put(
                (channel, "patchset-created", event))
            bot = GerritBot(
                gerrit_event_queues[uploader.username],
                host = IRC_HOST,
                port = IRC_PORT,
                nick = uploader.username,
                realname = uploader.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)


@actions.ActionRegistry.register("gerbage.CaptureChangeMerged")
class CaptureChangeMergedAction(actions.Action):
    def  _do_run(self, event, cfg, action_cfg, source):
        global gerrit_event_queues
        change = event.change
        submitter = event.submitter
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if submitter.username in gerrit_event_queues:
            gerrit_event_queues[submitter.username].put(
                (channel, "change-merged", event))
        else:
            gerrit_event_queues[submitter.username] = queue.Queue()
            gerrit_event_queues[submitter.username].put(
                (channel, "change-merged", event))
            bot = GerritBot(
                gerrit_event_queues[submitter.username],
                host = IRC_HOST,
                port = IRC_PORT,
                nick = submitter.username,
                realname = submitter.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)
