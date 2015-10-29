import gevent
import logging
import sys
import time

from gevent import monkey, queue, socket

monkey.patch_all()

IRC_CONNECTED = "001"
IRC_NICK_IN_USE = "433"
IRC_PING = "PING"
IRC_PRIVMSG = "PRIVMSG"


class GerritBot(object):
    """
    An IRC bot that will log into your server with the Gerrit username
    as its nick and relay Gerrit events to channels that map to project
    names.  The IRC-specific bits are based on a very helpful gist:

    https://gist.github.com/maxcountryman/676306

    """
    def __init__(self, gerrit_events, **kwargs):
        super(GerritBot, self).__init__()

        settings = dict(kwargs)
        self.host = settings["host"]
        self.port = settings["port"]
        self.channels = settings["channels"]
        self.nick = settings["nick"]
        self.realname = settings["realname"]
        self.gerrit_events = gerrit_events

    def _connect(self):
        self.connection = TCPConnection(self.host, self.port)
        gevent.spawn(self.connection.connect)
        self.do_nick()
        self.do_user()

    def _disconnect(self):
        self.connection.disconnect()

    def _gerrit_event_loop(self):
        try:
            while True:
                try:
                    channel, event_type, event_data = self.gerrit_events.get()
                except gevent.queue.Queue.Empty:
                    pass
                except ValueError:
                    logging.error("Invalid Gerrit event put into queue. Eek!")
                else:
                    if channel not in self.channels:
                        self.channels.append(channel)
                        self.do_join(channel)
                    time.sleep(2)
                    if event_type == "patchset-created":
                        self._handle_patchset_created_event(channel, event_data)
                    elif event_type == "change-merged":
                        self._handle_change_merged_event(channel, event_data)
        except Exception as e:
            logging.error(str(e))
            sys.exit(1)

    def _handle_patchset_created_event(self, channel, data):
        change = data.change
        patchset = data.patchSet
        self.do_privmsg(
            channel,
            "[patchset-created] subject: {0}, change: {1}, revision: {2}, "
            "url: {3}".format(
                change.subject,
                change.number,
                patchset.number,
                change.url
            )
        )

    def _handle_change_merged_event(self, channel, data):
        change = data.change
        patchset = data.patchSet
        self.do_privmsg(
            channel,
            "[change-merged] subject: {0}, change: {1}, revision: {2}, "
            "url: {3}".format(
                change.subject,
                change.number,
                patchset.number,
                change.url
            )
        )

    def _irc_event_loop(self):
        try:
            while True:
                line = self.connection.input_queue.get()
                logging.debug(line)
                prefix, command, args = self._parse(line)
                if command == IRC_CONNECTED:
                    [self.do_join(channel) for channel in self.channels]
                elif command == IRC_NICK_IN_USE:
                    self.do_nick(self.nick + "_")
                elif command == IRC_PING:
                    self.do_pong(args)
        except Exception as e:
            logging.error(str(e))
            sys.exit(1)

    def _parse(self, s):
        prefix = ""
        trailing = []
        if not s:
            logging.debug("Received an empty line from the host.")
            return
        if s[0] == ":":
            prefix, s = s[1:].split(" ", 1)
        if s.find(" :") != -1:
            s, trailing = s.split(" :", 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args

    def _send(self, s):
        self.connection.output_queue.put(s)

    def _send_command(self, command, args, prefix=None):
        if prefix:
            self._send(prefix + command + " " + "".join(args))
        else:
            self._send(command + " " + "".join(args))

    def connect(self):
        self._connect()
        gevent.joinall([
            gevent.spawn(self._irc_event_loop),
            gevent.spawn(self._gerrit_event_loop)
        ])

    def do_join(self, channel):
        self._send_command("JOIN", channel)

    def do_nick(self, nick=None):
        if nick:
            self.nick = nick
        self._send_command("NICK", self.nick)

    def do_privmsg(self, target, msg):
        self._send_command("PRIVMSG", (target + " :" + msg))

    def do_pong(self, args):
        self._send_command("PONG", args)

    def do_user(self):
        self._send_command('USER', (self.nick, ' 3 ', '* ', self.realname))


class TCPConnection(object):
    def __init__(self, host, port, timeout=300):
        self.host = host
        self.port = port
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self._input_buffer = ""
        self._output_buffer = ""
        self._socket = socket.socket()
        self.timeout = timeout

    def _recv_loop(self):
        while True:
            data = self._socket.recv(4096)
            self._input_buffer += data
            while "\r\n" in self._input_buffer:
                line, self._input_buffer = self._input_buffer.split("\r\n", 1)
                self.input_queue.put(line)

    def _send_loop(self):
        while True:
            line = self.output_queue.get().splitlines()[0][:500]
            self._output_buffer += line.encode("utf-8", "replace") + "\r\n"
            while self._output_buffer:
                sent = self._socket.send(self._output_buffer)
                self._output_buffer = self._output_buffer[sent:]

    def connect(self):
        self._socket.connect((self.host, self.port))
        try:
            jobs = [gevent.spawn(self._recv_loop), gevent.spawn(self._send_loop)]
            gevent.joinall(jobs)
        finally:
            gevent.killall(jobs)

    def disconnect(self):
        self._socket.close()

