# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import re
from wurfl_python import constants
from wurfl_python import normalizers
from wurfl_python import handlers


class Android(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Android'.
    '''
    def normalize(self, ua):
        ua = re.sub(r'(Android)[ \-](\d\.\d)([^; \/\)]+)', r'\1 \2', ua)
        skip_normalization = [
            u'Opera Mini',
            u'Opera Mobi',
            u'Opera Tablet',
            u'Fennec',
            u'Firefox',
            u'UCWEB7',
            u'NetFrontLifeBrowser/2.2',
        ]
        if not handlers.Utils.check_if_contains_any_of(ua, skip_normalization):
            model = handlers.AndroidHandler.get_android_model(ua, False)
            version = handlers.AndroidHandler.get_android_version(ua, False)
            if model is not None and version is not None:
                prefix = version + u' ' + model + constants.RIS_DELIMITER
                return prefix + ua
        return ua


class Chrome(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Chrome'.
    '''
    def normalize(self, ua):
        return self._chrome_with_major_version(ua)

    def _chrome_with_major_version(self, ua):
        start_idx = ua.find(u'Chrome')
        if start_idx > 0:
            end_idx = ua.find(u'.', start_idx)
            if end_idx == -1:
                return ua[start_idx:]
            else:
                return ua[start_idx:end_idx]
        return ua


class Firefox(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Firefox'.
    '''
    def normalize(self, ua):
        return self._firefox_with_major_and_minor_version(ua)

    def _firefox_with_major_and_minor_version(self, ua):
        index = ua.find(u'Firefox')
        if index > 0:
            return ua[index:]
        return ua


class HTCMac(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_HTCMac'.
    '''
    def normalize(self, ua):
        model = handlers.HTCMacHandler.get_htcmac_model(ua)
        if model is not None:
            prefix = model + constants.RIS_DELIMITER
            return prefix + ua
            pass
        return ua


class Kindle(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Kindle'.
    '''
    def normalize(self, ua):
        if handlers.Utils.check_if_contains_all(ua, [u'Android', u'Kindle Fire']):
            model = handlers.AndroidHandler.get_android_model(ua, False)
            version = handlers.AndroidHandler.get_android_version(ua, False)
            if model is not None and version is not None:
                prefix = version + ' ' + model + constants.RIS_DELIMITER
                return prefix + ua
        return ua


class Konqueror(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Konqueror'.
    '''
    KONQUEROR = u'Konqueror'

    def normalize(self, ua):
        return self._konqueror_with_major_version(ua)

    def _konqueror_with_major_version(self, ua):
        index = ua.find(self.KONQUEROR)
        if index > 0:
            return ua[index:index+10]
        return ua


class LG(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_LG'.
    '''
    def normalize(self, ua):
        index = ua.find(u'LG')
        if index > 0:
            return ua[index:]
        return ua


class LGUPLUS(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_LGUPLUS'.
    '''
    LGPLUS_PATTERN = r'Mozilla.*(Windows (?:NT|CE)).*(POLARIS|WV).*lgtelecom;.*;(.*);.*'

    def normalize(self, ua):
        return re.sub(self.LGPLUS_PATTERN, r'\3 \1 \2', ua)


class MSIE(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_MSIE'.
    '''
    def normalize(self, ua):
        return self._msie_with_version(ua)

    def _msie_with_version(self, ua):
        index = ua.find(u'MSIE')
        if index > 0:
            return ua[index:index + 8]
        return ua


class Opera(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Opera'.
    '''
    def normalize(self, ua):
        # Repair Opera user agents using fake version 9.80
        # Normalize: Opera/9.80 (X11; Linux x86_64; U; sv) Presto/2.9.168 Version/11.50
        # Into: Opera/11.50 (X11; Linux x86_64; U; sv) Presto/2.9.168 Version/11.50
        if handlers.Utils.check_if_starts_with(ua, u'Opera/9.80'):
            matches = re.search(r'Version/(\d+\.\d+)', ua)
            if matches is not None:
                ua = ua.replace(u'Opera/9.80', u'Opera/' + matches.group(1))
        return ua


class Safari(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_Safari'.
    '''
    PATTERN = r'(Mozilla\/5\.0.*U;)(?:.*)(Safari\/\d{0,3})(?:.*)'

    def normalize(self, ua):
        return ua


class WebOS(normalizers.Interface):
    '''
    @see WURFL PHP 'WURFL_Request_UserAgentNormalizer_Specific_WebOS'.
    '''
    def normalize(self, ua):
        model = handlers.WebOSHandler.get_webos_model_version(ua)
        os_ver = handlers.WebOSHandler.get_webos_version(ua)
        if model is not None and os_ver is not None:
            prefix = model + ' ' + os_ver + constants.RIS_DELIMITER
            return prefix + ua
        return ua
