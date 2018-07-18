import os
import lx
import modo
import re
from datetime import date, datetime

keywords = ['scene',
            'file',
            'item',
            'ext',
            'date',
            'hour',
            '#'
            ]


def generate_increment(increment, padding):
    string = format(increment, '0%s' % padding)
    return string


def slice(pattern, increment):
    sliced_in = pattern.split('<')

    sliced = []

    for s in sliced_in:
        sliced_out = s.split('>')
        for ss in sliced_out:
            if ss is not '':
                if '#' in ss:
                    padding = ss.count('#')
                    number = generate_increment(increment, padding)
                    start = ss.find('#')
                    ss = ss[:start] + number + ss[start+padding:]
                sliced.append(ss.lower())

    return sliced


def construct_filename(self, item, pattern, filename, ext, increment):

    scnName = os.path.splitext(self.scnName)[0]

    today = str(date.today())
    now = str(datetime.now().time().hour)+':'+str(datetime.now().time().minute)

    kw = {keywords[0]: scnName,
          keywords[1]: filename,
          keywords[2]: item,
          keywords[3]: ext,
          keywords[4]: today,
          keywords[5]: now}

    sliced = slice(pattern, increment)

    construced_filename = ''

    for s in sliced:
        if s in keywords:
            construced_filename += kw[s]
        else:
            construced_filename += s

    return construced_filename
