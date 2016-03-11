from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy
import pdfrw

from twisted.internet import defer

from mock import Mock, patch
from testtools import ExpectedException, TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_pdf.proc import LoadPdfPages


class LoadPdfPagesTestCase(TestCase):
    def test_load_all(self):
        sut = LoadPdfPages(key='test_path', destkey='test_content')
        insert = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'test_path': '/path/to/some/file.pdf'
                }
            }
        }

        expected = copy.deepcopy(insert)
        expected['data']['a']['test_content'] = tuple([
            'pdf content of page 1',
            'pdf content of page 2',
            'pdf content of page 3'
        ])
        matches = MatchesSendDeltaItemInvocation(expected, sut)
        send = Mock(spec=Scheduler.send)

        with patch('pdfrw.PdfReader', spec=pdfrw.PdfReader) as reader_mock:
            reader_mock.return_value.pages = [
                'pdf content of page 1',
                'pdf content of page 2',
                'pdf content of page 3'
            ]
            sut(insert, send)

        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

        reader_mock.assert_called_with('/path/to/some/file.pdf')

    def test_load_some(self):
        sut = LoadPdfPages(slicekey='test_slice')
        insert = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'path': '/path/to/some/file.pdf',
                    'test_slice': slice(1, 5, 2)
                }
            }
        }

        expected = copy.deepcopy(insert)
        expected['data']['a']['content'] = tuple([
            'pdf content of page 2',
            'pdf content of page 4'
        ])
        matches = MatchesSendDeltaItemInvocation(expected, sut)
        send = Mock(spec=Scheduler.send)

        with patch('pdfrw.PdfReader', spec=pdfrw.PdfReader) as reader_mock:
            reader_mock.return_value.pages = [
                'pdf content of page 1',
                'pdf content of page 2',
                'pdf content of page 3',
                'pdf content of page 4',
                'pdf content of page 5',
                'pdf content of page 6'
            ]
            sut(insert, send)

        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

        reader_mock.assert_called_with('/path/to/some/file.pdf')

    def test_load_with_existing_reader(self):
        reader_mock = Mock(spec=pdfrw.PdfReader)
        reader_mock.pages = [
            'pdf content of page 1',
            'pdf content of page 2',
            'pdf content of page 3'
        ]

        sut = LoadPdfPages(key='test_reader')
        insert = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'test_reader': reader_mock
                }
            }
        }

        # Cannot deepcopy pdfrw.PdfReader objects
        #expected = copy.deepcopy(insert)
        expected = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'test_reader': reader_mock,
                    'content': tuple([
                        'pdf content of page 1',
                        'pdf content of page 2',
                        'pdf content of page 3'
                    ])
                }
            }
        }
        matches = MatchesSendDeltaItemInvocation(expected, sut)
        send = Mock(spec=Scheduler.send)

        sut(insert, send)

        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

        self.assertEquals(reader_mock.call_count, 0)
