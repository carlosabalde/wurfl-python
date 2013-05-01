# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from wurfl_python.handlers import matchers
import Levenshtein


class LDMatcher(matchers.Interface):
    '''
    @see WURFL PHP 'WURFL_Handlers_Matcher_LDMatcher'.
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LDMatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def INSTANCE(cls):
        return cls()

    def match(self, collection, needle, tolerance):
        best = tolerance
        match = u''
        for ua in collection:
            if abs(len(needle) - len(ua)) <= tolerance:
                current = Levenshtein.distance(needle, ua)
                if current <= best:
                    best = current - 1
                    match = ua
        return match
