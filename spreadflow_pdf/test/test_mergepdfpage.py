from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy
import pdfrw

from mock import Mock, patch, call
from testtools import TestCase

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_pdf.proc import MergePdfPage


class MergPdfPageTestCase(TestCase):
    def test_merge(self):
        sut = MergePdfPage(key='test_content', destkey='test_merged_content')
        insert = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'test_content': [
                        'pdf page content',
                        'pdf watermark content'
                    ],
                }
            }
        }

        expected = copy.deepcopy(insert)
        expected['data']['a']['test_merged_content'] = ('pdf page with watermark',)
        matches = MatchesSendDeltaItemInvocation(expected, sut)
        send = Mock(spec=Scheduler.send)

        merge_mock = Mock(spec=pdfrw.PageMerge)
        merge_mock.return_value.render.return_value = 'pdf page with watermark'

        with patch('pdfrw.PageMerge', merge_mock):
            sut(insert, send)

        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

        merge_mock.assert_has_calls([
            call(),
            call().add('pdf page content'),
            call().add('pdf watermark content'),
            call().render()
        ])
