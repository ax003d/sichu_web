# ucsv - a drop-in extension of CSV module to read and write Unicode files

'''

A drop-in extension of CSV module to read and write Unicode files

ABSTRACT

    The standard CSV module can read/parse and write standard ASCII
    files with comma-separated values (CSV).  This module is an
    extension/wrapper to read and write comma-separated value files in
    UTF-8 or other encodings.

    Much of the code is stolen from an example in the 2.5.2 Python
    Library Reference, with additional wrappers for Unicode-ready
    DictReader, DictWriter.  In addition, the reader tries to turn
    things that look like numbers into actual numerical values, and
    interpolates non-strings into strings suitable for the writer.

    This is a "drop in" extension for the normal CSV module.

SYNOPSIS

    >>> import ucsv as csv

AUTHOR

    Ed Halley (ed@halley.cc) 18 August 2009

'''

#----------------------------------------------------------------------------

import csv ; from csv import *

__version__ = '1.0 Unicode'
__dropins__ = [ 'reader', 'writer', 'DictReader', 'DictWriter' ]

import codecs
import cStringIO

class UTF8Recoder:
    '''Iterator that reads a stream encoded in any given encoding.
    The output is reencoded to UTF-8 for internal consistency.
    '''
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class reader:
    '''A CSV reader which will iterate over lines in the CSV file "f",
    from content in the optional encoding.
    '''

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def value(self, s):
        try: return int(s)
        except: pass
        try: return float(s)
        except: pass
        return unicode(s, "utf-8")

    def next(self):
        row = self.reader.next()
        return [ self.value(s) for s in row ]

    def __iter__(self):
        return self

class writer:
    '''A CSV writer which will write rows to CSV file "f",
    employing the given encoding.
    '''

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.lookup(encoding)[-1](f)

    def writerow(self, row):
        self.writer.writerow( [ (u'%s'%s).encode("utf-8") for s in row ] )
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        self.encoder.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class DictReader:
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.reader = reader(f, dialect, *args, **kwds)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        if self.fieldnames is None:
            self.fieldnames = row
            row = self.reader.next()

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = self.reader.next()
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d

class DictWriter:
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError, \
                  ("extrasaction (%s) must be 'raise' or 'ignore'" %
                   extrasaction)
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)
        self.writer.writerow(fieldnames)

    def _dict_to_list(self, rowdict):
        if self.extrasaction == "raise":
            for k in rowdict.keys():
                if k not in self.fieldnames:
                    raise ValueError, "dict contains fields not in fieldnames"
        return [rowdict.get(key, self.restval) for key in self.fieldnames]

    def writerow(self, rowdict):
        return self.writer.writerow(self._dict_to_list(rowdict))

    def writerows(self, rowdicts):
        rows = []
        for rowdict in rowdicts:
            rows.append(self._dict_to_list(rowdict))
        return self.writer.writerows(rows)


