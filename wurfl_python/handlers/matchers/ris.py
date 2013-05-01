# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from wurfl_python.handlers import matchers


class RISMatcher(matchers.Interface):
    '''
    @see WURFL PHP 'WURFL_Handlers_Matcher_RISMatcher'.
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RISMatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def INSTANCE(cls):
        return cls()

    def match(self, collection, needle, tolerance):
        match = None
        best_distance = 0
        low = 0
        high = len(collection) - 1
        best_index = 0

        while low <= high:
            mid = int(round(low + high) / 2)
            find = collection[mid]
            distance = self._longest_common_prefix_length(needle, find)
            if distance >= tolerance and distance > best_distance:
                best_index = mid
                match = find
                best_distance = distance

            cmp = (find > needle) - (find < needle)
            if cmp < 0:
                low = mid + 1
            elif cmp > 0:
                high = mid - 1
            else:
                break

        if best_distance < tolerance:
            return None
        if best_index == 0:
            return match
        return self._first_of_the_bests(collection, needle, best_index, best_distance)

    def _first_of_the_bests(self, collection, needle, best_index, best_distance):
        while best_index > 0 and self._longest_common_prefix_length(collection[best_index-1], needle) == best_distance:
            best_index = best_index - 1
        return collection[best_index]

    def _longest_common_prefix_length(self, s, t):
        length = min(len(s), len(t))
        i = 0
        while i < length:
            if s[i] != t[i]:
                break
            i = i + 1
        return i
