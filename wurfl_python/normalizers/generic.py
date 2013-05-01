# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import re
from wurfl_python import normalizers
from wurfl_python import handlers


class BabelFish(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_BabelFish'.
    '''
    BABEL_FISH_REGEX = r'\s*\(via babelfish.yahoo.com\)\s*'

    def normalize(self, ua):
        return re.sub(self.BABEL_FISH_REGEX, r'', ua)


class BlackBerry(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_BlackBerry'.
    '''
    def normalize(self, ua):
        # Normalize mixed-case BlackBerry.
        ua = re.sub(r'(?i)blackberry', r'BlackBerry', ua)
        index = ua.find(u'BlackBerry')
        if index > 0 and ua.find(u'AppleWebKit') == -1:
            return ua[index:]
        return ua


class LocaleRemover(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_LocaleRemover'.
    '''
    def normalize(self, ua):
        return handlers.Utils.remove_locale(ua)


class NovarraGoogleTranslator(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_NovarraGoogleTranslator'.
    '''
    NOVARRA_GOOGLE_TRANSLATOR_PATTERN = r'(\sNovarra-Vision.*)|(,gzip\(gfe\)\s+\(via translate.google.com\))'

    def normalize(self, ua):
        return re.sub(self.NOVARRA_GOOGLE_TRANSLATOR_PATTERN, r'', ua)


class SerialNumbers(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_SerialNumbers'.
    '''
    SERIAL_NUMBERS_PATTERN = r'(\[(TF|NT|ST)[\d|X]+\])|(\/SN[\d|X]+)'

    def normalize(self, ua):
        return re.sub(self.SERIAL_NUMBERS_PATTERN, r'', ua)


class UCWEB(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_UCWEB'.
    '''
    def normalize(self, ua):
        # Starts with 'JUC' or 'Mozilla/5.0(Linux;U;Android'.
        if ua.startswith(u'JUC') or ua.startswith(u'Mozilla/5.0(Linux;U;Android'):
            ua = re.sub(r'^(JUC \(Linux; U;)(?= \d)', r'\1 Android', ua)
            ua = re.sub(r'(Android|JUC|[;\)])(?=[\w|\(])', r'\1', ua)
        return ua


class UPLink(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_UPLink'.
    '''
    def normalize(self, ua):
        index = ua.find(u' UP.Link')
        if index > 0:
            return ua[0:index]
        return ua


class YesWAP(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Generic_YesWAP'.
    '''
    YES_WAP_REGEX = r'\s*Mozilla\/4\.0 \(YesWAP mobile phone proxy\)'

    def normalize(self, ua):
        return re.sub(self.YES_WAP_REGEX, r'', ua)
