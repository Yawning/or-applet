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

from subprocess import Popen
from gi.repository import Gtk,Gdk
from stem import CircBuildFlag,CircClosureReason,CircPurpose,CircStatus,HiddenServiceState

from orapplet.utils import get_leek_icon

def _pos(menu, icon):
    return (Gtk.StatusIcon.position_menu(menu, icon))

def _format_circuit(circuit):
    s  = 'Circuit:  ' + circuit.id + '\n'
    s += 'Created:  ' + str(circuit.created) + '\n'
    s += 'Status:   ' + _format_status(circuit.status) + '\n'
    s += 'Purpose:  ' + _format_purpose(circuit.purpose) + '\n'
    s += 'Flags: \n' + _format_build_flags(circuit.build_flags)
    if circuit.hs_state is not None:
        s += 'HS State: ' + _format_hs_state(circuit.hs_state) + '\n'
    if circuit.path is not None and circuit.path:
        s += 'Path:\n'
        s += _format_path(circuit.path)
    if circuit.reason is not None:
        s += 'Local Close Reason:  '  + _format_close_reason(circuit.reason)
    if circuit.remote_reason is not None:
        s += 'Remote Close Reason: ' + _format_close_reason(circuit.remote_reason)
    return s

_FORMAT_STATUSES = {
    CircStatus.LAUNCHED: 'LAUNCHED (circuit ID assigned to new circuit)',
    CircStatus.BUILT: 'BUILT (all hops finished, can now accept streams)',
    CircStatus.EXTENDED: 'EXTENDED (one more hop has been completed)',
    CircStatus.FAILED: 'FAILED (circuit closed (was not built))',
    CircStatus.CLOSED: 'CLOSED (circuit closed (was built))'
}

def _format_status(status):
    return _FORMAT_STATUSES.get(status, str(status))

_FORMAT_PURPOSES = {
    CircPurpose.GENERAL: 'GENERAL (circuit for AP and/or directory request streams)',
    CircPurpose.HS_CLIENT_INTRO: 'HS_CLIENT_INTRO (HS client-side introduction-point circuit)',
    CircPurpose.HS_CLIENT_REND: 'HS_CLIENT_REND (HS client-side rendezvous circuit; carries AP streams)',
    CircPurpose.HS_SERVICE_INTRO: 'HS_SERVICE_INTRO (HS service-side introduction-point circuit)',
    CircPurpose.HS_SERVICE_REND: 'HS_SERVICE_REND (HS service-side rendezvous circuit)',
    CircPurpose.TESTING: 'TESTING (reachability-testing circuit; carries no traffic)',
    CircPurpose.CONTROLLER: 'CONTROLLER (circuit built by a controller)',
    CircPurpose.MEASURE_TIMEOUT: 'MEASURE_TIMEOUT (circuit being kept around to see how long it takes)'
}

def _format_purpose(purpose):
    return _FORMAT_PURPOSES.get(purpose, str(purpose))

_FORMAT_FLAGS = {
    CircBuildFlag.ONEHOP_TUNNEL: 'ONEHOP_TUNNEL (one-hop circuit, used for tunneled directory conns)',
    CircBuildFlag.IS_INTERNAL: 'IS_INTERNAL (internal circuit, not to be used for exiting streams)',
    CircBuildFlag.NEED_CAPACITY: 'NEED_CAPACITY (this circuit must use only high-capacity nodes)',
    CircBuildFlag.NEED_UPTIME: 'NEED_UPTIME (this circuit must use only high-uptime nodes)'
}

def _format_build_flags(flags):
    s_list = []
    for flag in flags:
        s_list.append(' %s\n' % _FORMAT_FLAGS.get(flag, str(flag)))
    return ''.join(s_list)

def _format_path(path):
    s_list = []
    idx = 0
    for hop in path:
        s_list.append(' [%d]: %s~%s\n' % (idx, hop[0], hop[1]))
        idx += 1
    return ''.join(s_list)

_FORMAT_HS_STATE = {
    HiddenServiceState.HSCI_CONNECTING: 'HSCI_CONNECTING (connecting to intro point)',
    HiddenServiceState.HSCI_INTRO_SENT: 'HSCI_INTRO_SENT (sent INTRODUCE1; waiting for reply from IP)',
    HiddenServiceState.HSCI_DONE: 'HSCI_DONE (received reply from IP relay; closing)',
    HiddenServiceState.HSCR_CONNECTING: 'HSCR_CONNECTING (connecting to or waiting for reply from RP)',
    HiddenServiceState.HSCR_ESTABLISHED_IDLE: 'HSCR_ESTABLISHED_IDLE (established RP; waiting for introduction)',
    HiddenServiceState.HSCR_ESTABLISHED_WAITING: 'HSCR_ESTABLISHED_WAITING (introduction sent to HS; waiting for rend)',
    HiddenServiceState.HSCR_JOINED: 'HSCR_JOINED (connected to HS)',
    HiddenServiceState.HSSI_CONNECTING: 'HSSI_CONNECTING (connecting to intro point)',
    HiddenServiceState.HSSI_ESTABLISHED: 'HSSI_ESTABLISHED (established intro point)',
    HiddenServiceState.HSSR_CONNECTING: 'HSSR_CONNECTING (connecting to client\'s rend point)',
    HiddenServiceState.HSSR_JOINED: 'HSSR_JOINED (connected to client\'s RP circuit)',
}

def _format_hs_state(hs_state):
    return _FORMAT_HS_STATE.get(hs_state, str(hs_state))

def _format_close_reason(reason):
    # Fuck it, these shouldn't show up in normal use anyway.
    return str(reason)

def _format_streams(streams):
    s_list = []
    for stream in streams:
        s_list.append(' %s\n' % stream)
    return ''.join(s_list)

def _labeled_separator(label):
    box = Gtk.Box()
    label = Gtk.Label(label) # set_markup?
    box.pack_start(Gtk.HSeparator(), True, True, 0)
    box.pack_start(label, False, False, 2)
    box.pack_start(Gtk.HSeparator(), True, True, 0)
    item = Gtk.ImageMenuItem()
    item.set_property('child', box)
    item.set_sensitive(False)
    return item

class PopupMenu(object):
    _ctl = None
    _menu = None
    _status_icon = None

    def __init__(self, icon):
        self._ctl = icon._ctl
        self._status_icon = icon
        self._menu = Gtk.Menu()
        item = Gtk.MenuItem('Stem Prompt')
        item.connect('activate', self._on_prompt)
        self._menu.append(item)
        item = Gtk.MenuItem('Reload Tor Config')
        item.connect('activate', self._on_reload)
        self._menu.append(item)
        self._menu.append(Gtk.SeparatorMenuItem())
        item = Gtk.MenuItem('About')
        item.connect('activate', self._on_about)
        self._menu.append(item)
        self._menu.show_all()

    def popup(self, widget, button, time):
        self._menu.popup(None, None, _pos, self._status_icon._icon, button, time)

    def _on_prompt(self, widget, data=None):
        Popen('/usr/bin/urxvt -e python2 -c "from stem.interpreter import main; main()"', shell=True)

    def _on_reload(self, widget, data=None):
        self._ctl.reload()

    def _on_about(self, widget, data=None):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_program_name('or-applet')
        about_dialog.set_copyright('Copyright 2014 Yawning Angel')
        about_dialog.set_comments('A Gtk+ Tor System Tray applet.')
        about_dialog.set_version('0.0.1')
        about_dialog.set_authors(['Yawning Angel'])
        about_dialog.set_artists(['Robin Weatherall http://www.robinweatherall.eu'])
        about_dialog.run()
        about_dialog.destroy()

class ActivateMenu(object):
    _ctl = None
    _clipboard = None
    _menu = None
    _status_icon = None

    def __init__(self, icon):
        self._ctl = icon._ctl
        self._clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._status_icon = icon
        self._menu = Gtk.Menu()
        item = Gtk.MenuItem('NEWNYM')
        item.set_sensitive(self._ctl.is_newnym_available())
        item.connect('activate', self._on_newnym)
        self._menu.append(item)
        self._menu.append(Gtk.SeparatorMenuItem())
        self._build_dynamic_menu()
        self._menu.show_all()

    def popup(self, widget, button, time):
        self._menu.popup(None, None, _pos, self._status_icon._icon, button, time)

    def _build_dynamic_menu(self):
        circuits = self._ctl.get_circuits()
        if circuits is None:
            item = Gtk.MenuItem('No circuits established')
            item.set_sensitive(False)
            self._menu.append(item)
            return
        streams = self._ctl.get_streams()

        for circuit in circuits:
            self._build_circuit_menu(circuit, streams)

    def _build_circuit_menu(self, circuit, streams):
        # Skip displaying internal circuits, unless they are actually hidden
        # service circuits in disguise.
        if CircBuildFlag.IS_INTERNAL in circuit.build_flags:
            if (CircPurpose.HS_CLIENT_INTRO not in circuit.purpose) and (CircPurpose.HS_CLIENT_REND not in circuit.purpose):
                return
        circ_info = _format_circuit(circuit)

        our_streams = []
        if CircPurpose.HS_CLIENT_INTRO in circuit.purpose or CircPurpose.HS_CLIENT_REND in circuit.purpose:
            our_streams.append('[HS]: %s.onion' % circuit.rend_query)
        else:
            for stream in streams:
                if stream.circ_id == circuit.id:
                    our_streams.append('[%s]: %s' % (stream.id, stream.target))
        if not our_streams:
            our_streams.append('No streams established')
        stream_info = 'Streams:\n%s' %  _format_streams(our_streams)

        menu = Gtk.Menu()
        menu.append(_labeled_separator('Streams'))
        for s in our_streams:
            item = Gtk.MenuItem(s)
            menu.append(item)

        menu.append(_labeled_separator('Path'))
        idx = 0
        for hop in circuit.path:
            item_text = '[%d]: %s~%s' % (idx, hop[0], hop[1])
            item = Gtk.MenuItem(item_text)
            menu.append(item)
            idx += 1
        menu.append(Gtk.SeparatorMenuItem())

        item = Gtk.MenuItem('Copy to clipboard')
        item.connect('activate', self._on_copy_circuit, circ_info + stream_info)
        menu.append(item)

        item = Gtk.MenuItem('Circuit: ' + circuit.id)
        item.set_submenu(menu)
        self._menu.append(item)

    def _on_newnym(self, widget, data=None):
        self._ctl.newnym()

    def _on_copy_circuit(self, widget, data=None):
        self._clipboard.set_text(data, -1)

class OrStatusIcon(object):
    _ctl = None
    _icon = None
    _menu_popup = None
    _activate_menu = None

    def __init__(self, ctl):
        self._ctl = ctl

        self._menu_popup = PopupMenu(self)

        self._icon = Gtk.StatusIcon()
        self._icon.set_from_file(get_leek_icon())
        self._icon.connect('activate', self._on_activate)
        self._icon.connect('popup-menu', self._menu_popup.popup)
        self._icon.set_visible(True)

    def set_tooltip_text(self, text):
        self._icon.set_tooltip_text(text)

    def pos(self, menu, icon):
        return (Gtk.StatusIcon.position_menu(menu, icon))

    def _on_activate(self, widget, data=None):
        # Fucking python GCs the menu unless I stash it in a local.
        self._activate_menu = ActivateMenu(self)
        self._activate_menu.popup(self._activate_menu, 1, Gtk.get_current_event_time())

