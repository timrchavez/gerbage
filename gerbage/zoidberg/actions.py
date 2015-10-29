import gevent

from zoidberg import actions
from gerbage import event_queues
from gerbage.bot import GerritBot
from gevent import queue

from gevent import monkey; monkey.patch_all()


@actions.ActionRegistry.register("gerbage.CapturePatchsetCreated")
class CapturePatchsetCreatedAction(actions.Action):
    def _do_run(self, event, cfg, action_cfg, source):
        change = event.change
        uploader = event.uploader
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if uploader.username in event_queues:
            event_queues[uploader.username].put(
                (channel, "patchset-created", event))
        else:
            event_queues[uploader.username] = queue.Queue()
            event_queues[uploader.username].put(
                (channel, "patchset-created", event))
            bot = GerritBot(
                event_queues[uploader.username],
                host = "localhost",
                port = 4096,
                nick = uploader.username,
                realname = uploader.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)


@actions.ActionRegistry.register("gerbage.CaptureChangeMerged")
class CaptureChangeMergedAction(actions.Action):
    def  _do_run(self, event, cfg, action_cfg, source):
        change = event.change
        submitter = event.submitter
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if submitter.username in event_queues:
            event_queues[submitter.username].put(
                (channel, "change-merged", event))
        else:
            event_queues[submitter.username] = queue.Queue()
            event_queues[submitter.username].put(
                (channel, "change-merged", event))
            bot = GerritBot(
                event_queues[submitter.username],
                host = "localhost",
                port = 4096,
                nick = submitter.username,
                realname = submitter.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)
