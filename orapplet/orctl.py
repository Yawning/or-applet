#!/usr/bin/env python2

# This file is part of or-applet.
#
# or-applet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# or-applet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with or-applet.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GLib,Notify
from stem import SocketError
from stem.control import Controller,EventType,Signal,State

class OrCtl(object):
    _control = None
    _status_icon = None
    _notify = None

    def __init__(self):
        self._notify = Notify.Notification.new('or-applet', None, None)
        pass

    def set_status_icon(self, status_icon):
        self._status_icon = status_icon

    def start_loop(self):
        self._status_icon.set_tooltip_text('Stem: Connecting')
        GLib.timeout_add_seconds(1, self._on_connect)

    def newnym(self):
        if self.is_newnym_available():
            self._control.signal(Signal.NEWNYM)

    def is_newnym_available(self):
        if self._control is None:
            return False
        return self._control.is_newnym_available()

    def reload(self):
        if self._control is None:
            return
        self._control.signal(Signal.RELOAD)

    def get_circuits(self):
        if self._control is None:
            return None
        return self._control.get_circuits(default=None)

    def get_streams(self):
        if self._control is None:
            return None
        return self._control.get_streams(default=None)

    def _on_connect(self):
        try:
            self._control = Controller.from_port()
        except SocketError:
            try:
                self._control = Controller.from_socket_file()
            except SocketError:
                self._status_icon.set_tooltip_text('Failed to initialize stem')
                return True
        self._control.add_status_listener(self._on_status)
        self._status_icon.set_tooltip_text('Stem: Authenticating')
        GLib.timeout_add_seconds(1, self._on_auth)
        return False

    def _on_auth(self):
        try:
            self._control.authenticate()
            self._on_established()
            return False
        except Exception as e:
            self._status_icon.set_tooltip_text('Failed to authenticate: %s' %e)
            return True

    def _on_status(self, controller, state, timestamp):
        if state == State.CLOSED:
            self.notify('Stem: Closed', urgency=Notify.Urgency.CRITICAL)
            self._control.close()
            self._control = None
            self.start_loop()

    def _on_established(self):
        self._status_icon.set_tooltip_text('Stem: Established')
        self.notify('Stem: Established')

        # Hook the noteworthy events.
        self._control.add_event_listener(self._on_notice_event, EventType.NOTICE)
        self._control.add_event_listener(self._on_warn_event, EventType.WARN)
        self._control.add_event_listener(self._on_err_event, EventType.ERR)
        self._control.add_event_listener(self._on_bw_event, EventType.BW)
        self._control.add_event_listener(self._on_signal_event, EventType.SIGNAL)

    def _on_signal_event(self,event):
        self.notify('Tor - Signal', event.signal)

    def _on_notice_event(self, event):
        self.notify('Tor [NOTICE]', event.message)

    def _on_warn_event(self, event):
        self.notify('Tor [WARN]', event.message)

    def _on_err_event(self, event):
        self.notify('Tor [ERROR]', event.message)

    def _on_bw_event(self, event):
        r_kib = event.read / 1024
        w_kib = event.written / 1024
        self._status_icon.set_tooltip_text('Read: %s KiB/s Write: %s KiB/s' % (str(r_kib), str(w_kib)))

    def notify(self, summary, message=None, urgency=Notify.Urgency.NORMAL, timeout=3000):
        self._notify.update(summary, message, None)
        self._notify.set_timeout(timeout)
        self._notify.set_urgency(urgency)
        self._notify.show()
