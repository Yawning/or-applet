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

from gi.repository import Gtk,Notify

from orapplet.orctl import OrCtl
from orapplet.status_icon import OrStatusIcon
from orapplet.utils import get_leek_icon

def main():
    # Initialize libnotify.
    Notify.init('orapplet')

    # Initialize stem and the status icon.
    ctl = OrCtl(True)
    icon = OrStatusIcon(ctl)
    ctl.set_status_icon(icon)
    ctl.start_loop()

    # Enter the Gtk+ event loop.
    Gtk.Window.set_default_icon_from_file(get_leek_icon())
    Gtk.main()

if __name__ == '__main__':
    main()

