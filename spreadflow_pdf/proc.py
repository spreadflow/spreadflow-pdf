# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import pdfrw
import tempfile

from spreadflow_delta.proc import ExtractorBase

class LoadPdfPages(ExtractorBase):
    def __init__(self, key='path', slicekey=None, destkey='content'):
        self.key = key
        self.destkey = destkey
        self.slicekey = slicekey

    def extract(self, key, doc):
        path_or_reader = doc[self.key]
        if hasattr(path_or_reader, 'pages'):
            reader = path_or_reader
        else:
            reader = pdfrw.PdfReader(path_or_reader)

        if self.slicekey is not None:
            slc = doc[self.slicekey]
            doc[self.destkey] = tuple(reader.pages[slc.start:slc.stop:slc.step])
        else:
            doc[self.destkey] = tuple(reader.pages)


class SavePdfPages(ExtractorBase):
    def __init__(self, key='content', destkey='savepath', clear=False, version='1.3', compress=False):
        self.key = key
        self.destkey = destkey
        self.clear = clear
        self.version = str(version)
        self.compress = compress

    def extract(self, key, doc):
        path = doc[self.destkey]
        tmpdir = os.path.dirname(path)

        stream = tempfile.NamedTemporaryFile(dir=tmpdir, delete=False)
        try:
            with stream:
                writer = pdfrw.PdfWriter(version=self.version, compress=self.compress)
                for page in doc[self.key]:
                    writer.addpage(page)
                writer.write(stream)
        except:
            os.unlink(stream.name)
            raise
        else:
            os.rename(stream.name, path)

        if self.clear:
            del doc[self.key]


class MergePdfPage(ExtractorBase):
    def __init__(self, key='content', destkey='content'):
        self.key = key
        self.destkey = destkey

    def extract(self, key, doc):
        result = pdfrw.PageMerge()
        for page in doc[self.key]:
            result.add(page)
        doc[self.destkey] = (result.render(),)
