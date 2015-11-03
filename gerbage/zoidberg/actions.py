import gevent

from gevent import monkey, queue
from zoidberg import actions

from gerbage.bot import GerritBot
from gerbage.queues import event_queues
from gerbage.settings import IRC_HOST, IRC_PORT

monkey.patch_all()

def get_nickname(username):
    return username.replace(".", "_")


@actions.ActionRegistry.register("gerbage.CapturePatchsetCreated")
class CapturePatchsetCreatedAction(actions.Action):
    def _do_run(self, event, cfg, action_cfg, source):
        change = event.change
        nickname = get_nickname(event.uploader.username)
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if nickname in event_queues:
            event_queues[nickname].put(
                (channel, "patchset-created", event))
        else:
            event_queues[nickname] = queue.Queue()
            event_queues[nickname].put(
                (channel, "patchset-created", event))
            bot = GerritBot(
                event_queues[nickname],
                host = IRC_HOST,
                port = IRC_PORT,
                nick = nickname,
                realname = event.uploader.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)


@actions.ActionRegistry.register("gerbage.CaptureChangeMerged")
class CaptureChangeMergedAction(actions.Action):
    def  _do_run(self, event, cfg, action_cfg, source):
        change = event.change
        submitter = get_nickname(event.submitter.username)
        channel = "#" + change.project

        # FIXME: Sanitize Gerrit username for IRC nick
        if nickname in event_queues:
            event_queues[nickname].put(
                (channel, "change-merged", event))
        else:
            event_queues[nickname] = queue.Queue()
            event_queues[nickname].put(
                (channel, "change-merged", event))
            bot = GerritBot(
                event_queues[nickname],
                host = IRC_HOST,
                port = IRC_PORT,
                nick = nickname,
                realname = event.submitter.name,
                channels = [channel]
            )
            gevent.spawn(bot.connect)
