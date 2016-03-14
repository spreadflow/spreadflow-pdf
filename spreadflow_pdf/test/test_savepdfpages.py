from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy
import pdfrw

from twisted.internet import defer

from mock import Mock, patch, mock_open, call
from testtools import ExpectedException, TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_pdf.proc import SavePdfPages


class SavePdfPagesTestCase(TestCase):
    def test_save(self):
        sut = SavePdfPages(key='test_content', destkey='test_savepath')
        insert = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'test_content': [
                        'pdf content of page 1',
                        'pdf content of page 2',
                        'pdf content of page 3'
                    ],
                    'test_savepath': '/path/to/some/dumpfile.pdf'
                }
            }
        }

        expected = copy.deepcopy(insert)
        matches = MatchesSendDeltaItemInvocation(expected, sut)
        send = Mock(spec=Scheduler.send)

        open_mock = mock_open()
        with patch('spreadflow_delta.util.open_replace', open_mock), patch('pdfrw.PdfWriter', spec=pdfrw.PdfWriter) as writer_mock:
            sut(insert, send)

        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

        open_mock.assert_called_once_with('/path/to/some/dumpfile.pdf')

        writer_mock.assert_called_with(version='1.3', compress=False)
        writer_mock.return_value.assert_has_calls([
            call.addpage(u'pdf content of page 1'),
            call.addpage(u'pdf content of page 2'),
            call.addpage(u'pdf content of page 3'),
            call.write(open_mock())
        ])
