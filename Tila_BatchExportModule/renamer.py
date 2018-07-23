import os
import modo
from datetime import date, datetime


class Renamer():
    keywords = ['scene',
                'file',
                'item',
                'ext',
                'date',
                'hour',
                '#'
                ]

    def __init__(self):
        self.scnName = modo.scene.current().name

    @staticmethod
    def generate_increment(increment, padding):
        string = format(increment, '0%s' % padding)
        return string

    def slice(self, pattern, increment):
        sliced_in = pattern.split('<')

        sliced = []

        for s in sliced_in:
            sliced_out = s.split('>')
            for ss in sliced_out:
                if ss is not '':
                    if '#' in ss:
                        padding = ss.count('#')
                        number = self.generate_increment(increment, padding)
                        start = ss.find('#')
                        ss = ss[:start] + number + ss[start + padding:]
                    sliced.append(ss.lower())

        return sliced

    def construct_filename(self, item, pattern, filename, ext, increment):

        scnName = os.path.splitext(self.scnName)[0]

        today = str(date.today())
        now = str(datetime.now().time().hour) + ':' + str(datetime.now().time().minute)

        kw = {self.keywords[0]: scnName,
              self.keywords[1]: filename,
              self.keywords[2]: item,
              self.keywords[3]: ext,
              self.keywords[4]: today,
              self.keywords[5]: now}

        sliced = self.slice(pattern, increment)

        construced_filename = ''

        for s in sliced:
            if s in self.keywords:
                construced_filename += kw[s]
            else:
                construced_filename += s

        return construced_filename
