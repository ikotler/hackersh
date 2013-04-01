# Copyright (C) 2013 Itzik Kotler
#
# This file is part of Hackersh.
#
# Hackersh is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# Hackersh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hackersh; see the file COPYING.  If not,
# see <http://www.gnu.org/licenses/>.

import os
import fcntl
import termios
import struct
import textwrap
import prettytable


# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python/566752#566752

def __ioctl_GWINSZ(fd):

    cr = None

    try:

        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))

    except Exception:

        pass

    return cr


def terminalsize():

    cr = __ioctl_GWINSZ(0) or __ioctl_GWINSZ(1) or __ioctl_GWINSZ(2)

    if not cr:

        try:

            fd = os.open(os.ctermid(), os.O_RDONLY)

            cr = __ioctl_GWINSZ(fd)

            os.close(fd)

        except:

            try:

                cr = (os.environ['LINES'], os.environ['COLUMNS'])

            except:

                cr = (25, 80)

    return int(cr[1]), int(cr[0])


def draw_underline(string):

    return string + '\n' + '-' * len(string) + '\n'


def __mk_tbl(fields):

    tbl = prettytable.PrettyTable(fields, left_padding_width=1, right_padding_width=1, hrules=prettytable.ALL)

    col_max_width = (terminalsize()[0] / len(fields)) - 30

    for k in tbl.align:

        tbl.align[k] = 'l'

    return (tbl, col_max_width)


def draw_static_tbl(data, fields, values):

    (tbl, col_max_width) = __mk_tbl(fields)

    for dataset in data:

        row_data = []

        for value in values:

            row_data.append('\n'.join(textwrap.wrap(dataset.get(value, '<N/A>'), col_max_width)))

        tbl.add_row(row_data)

    return tbl.get_string()


def draw_dict_tbl(dct, fields, keys):

    (tbl, col_max_width) = __mk_tbl(fields)

    for key in keys:

        row_data = [str(key).title()]

        row_data.append('\n'.join(textwrap.wrap(str(dct.get(key, '<N/A>')), col_max_width)))

        tbl.add_row(row_data)

    return tbl.get_string()


def draw_msgbox(string):

    msgbox = '\n'
    msgbox += '*' * 80 + '\n'
    msgbox += '*' + ' '.ljust(78) + '*' + '\n'
    msgbox += '*' + ' '.ljust(78) + '*' + '\n'
    msgbox += '*  ' + string.ljust(76) + '*' + '\n'
    msgbox += '*' + ' '.ljust(78) + '*' + '\n'
    msgbox += '*' + ' '.ljust(78) + '*' + '\n'
    msgbox += '*' * 80 + '\n'

    return msgbox
