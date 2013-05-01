# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from abc import ABCMeta


class Interface(object):
    '''
    @see WURFL PHP 'WURFL_Handlers_Matcher_Interface'.
    '''
    __metaclass__ = ABCMeta

    def match(collection, needle, tolerance):
        '''
        Attempts to find a matching needle in given collection within the
        specified tolerance.
        '''
        raise NotImplementedError('Please implement this method')
