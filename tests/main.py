# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import sys
import unittest
try:
    import wurfl
    import uas
except ImportError:
    sys.stderr.write("\nForgot to run 'make dump'? Please, check out the documentation.\n\n")
    sys.exit(1)


class MainTestCase(unittest.TestCase):
    def runTest(self):
        index = 0
        for (ua, id) in uas.UAS:
            device = wurfl.match(ua)
            self.assertEqual(id, device.id, 'Device detection mismatch:\n  INDEX: %d / %d\n  UA: %s\n  WURLF PHP: %s\n  WURFL PYTHON: %s\n' % (
                index,
                len(uas.UAS),
                ua,
                id,
                device.id))
            index += 1
