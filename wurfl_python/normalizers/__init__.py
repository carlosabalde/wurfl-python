# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from abc import ABCMeta
import copy


class Interface(object):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Interface'.
    '''
    __metaclass__ = ABCMeta

    def normalize(self, ua):
        raise NotImplementedError('Please implement this method')


class Null(Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Null'.
    '''
    def normalize(self, ua):
        return ua


class UserAgentNormalizer(Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer'.
    '''
    def __init__(self, normalizers=[]):
        self._normalizers = normalizers

    def add_normalizer(self, normalizer):
        normalizers = copy.copy(self._normalizers)
        normalizers.append(normalizer)
        return UserAgentNormalizer(normalizers)

    def normalize(self, ua):
        normalized_ua = ua
        for normalizer in self._normalizers:
            normalized_ua = normalizer.normalize(normalized_ua)
        return normalized_ua
