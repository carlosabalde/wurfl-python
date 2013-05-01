# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import re
import math
from collections import OrderedDict
from abc import ABCMeta
from wurfl_python import constants
from wurfl_python import normalizers
from wurfl_python.handlers.matchers.ld import LDMatcher
from wurfl_python.handlers.matchers.ris import RISMatcher


class Handler(object):
    '''
    @see WURFL PHP 'WURFL_Handlers_Handler'.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, normalizer=None):
        if normalizer is None:
            self._normalizer = normalizers.Null()
        else:
            self._normalizer = normalizer
        self._uas_with_device_id = {}
        self._ordered_uas = None
        self._next_handler = None

    def set_next_handler(self, handler):
        self._next_handler = handler

    def can_handle(self, ua):
        '''
        Returns True if this handler can handle the given ua.
        '''
        raise NotImplementedError('Please implement this method')

    def filter(self, ua, device_id):
        if self.can_handle(ua):
            self._uas_with_device_id[self._normalizer.normalize(ua)] = device_id
            self._ordered_uas = None
            return None

        if self._next_handler is not None:
            return self._next_handler.filter(ua, device_id)

        return None

    def match(self, ua):
        '''
        Returns a matching device id for the given ua, if no matching
        device is found will return 'generic'.
        '''
        if self.can_handle(ua):
            return self.apply_match(ua)

        if self._next_handler is not None:
            return self._next_handler.match(ua)

        return constants.GENERIC

    def apply_match(self, ua):
        # Normalize.
        ua = self._normalizer.normalize(ua)
        # Start with an Exact match.
        device_id = self.apply_exact_match(ua)
        # Try with the conclusive Match.
        if self._is_blank_or_generic(device_id):
            device_id = self.apply_conclusive_match(ua)
            # Try with recovery match.
            if self._is_blank_or_generic(device_id):
                device_id = self.apply_recovery_match(ua)
                # Try with catch all recovery Match.
                if self._is_blank_or_generic(device_id):
                    device_id = self.apply_recovery_catch_all_match(ua)
                    # All attempts to match have failed.
                    if self._is_blank_or_generic(device_id):
                        device_id = constants.GENERIC
        # Done!
        return device_id

    def apply_exact_match(self, ua):
        if ua in self._uas_with_device_id:
            return self._uas_with_device_id[ua]
        return constants.NO_MATCH

    def apply_conclusive_match(self, ua):
        match = self.look_for_matching_ua(ua)
        if match:
            return self._uas_with_device_id[match]
        return constants.NO_MATCH

    def look_for_matching_ua(self, ua):
        tolerance = Utils.first_slash(ua)
        return Utils.ris_match(self._get_ordered_uas(), ua, tolerance)

    def apply_recovery_match(self, ua):
        pass

    def apply_recovery_catch_all_match(self, ua):
        if Utils.is_desktop_browser_heavy_duty_analysis(ua):
            return constants.GENERIC_WEB_BROWSER
        mobile = Utils.is_mobile_browser(ua)
        desktop = Utils.is_desktop_browser(ua)
        if not desktop:
            device_id = Utils.get_mobile_catch_all_id(ua)
            if device_id != constants.NO_MATCH:
                return device_id
        if mobile:
            return constants.GENERIC_MOBILE
        if desktop:
            return constants.GENERIC_WEB_BROWSER
        return constants.GENERIC

    def get_device_id_from_ris(self, ua, tolerance):
        match = Utils.ris_match(self._get_ordered_uas(), ua, tolerance)
        if match:
            return self._uas_with_device_id[match]
        return constants.NO_MATCH

    def get_device_id_from_ld(self, ua, tolerance=None):
        match = Utils.ld_match(self._get_ordered_uas(), ua, tolerance)
        if match:
            return self._uas_with_device_id[match]
        return constants.NO_MATCH

    def _is_blank_or_generic(self, device_id):
        return \
            device_id is None or \
            device_id == constants.GENERIC or \
            len(device_id.strip()) == 0

    def _get_ordered_uas(self):
        if self._ordered_uas is None:
            self._ordered_uas = self._uas_with_device_id.keys()
            self._ordered_uas.sort()
        return self._ordered_uas


class Chain(Handler):
    '''
    @see WURFL PHP 'WURFL_UserAgentHandlerChain'.
    '''
    def __init__(self):
        super(Chain, self).__init__()
        self._handlers = []

    def add_handler(self, handler):
        size = len(self._handlers)
        if size > 0:
            self._handlers[size-1].set_next_handler(handler)
        self._handlers.append(handler)
        return self

    def filter(self, ua, device_id):
        Utils.reset()
        return self._handlers[0].filter(ua, device_id)

    def match(self, ua):
        Utils.reset()
        return self._handlers[0].match(ua)


class AlcatelHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_AlcatelHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with(ua, u'Alcatel') or\
            Utils.check_if_starts_with(ua, u'ALCATEL')


class AndroidHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_AndroidHandler'.
    '''
    constant_ids = [
        u'generic_android',
        u'generic_android_ver1_5',
        u'generic_android_ver1_6',
        u'generic_android_ver2',
        u'generic_android_ver2_1',
        u'generic_android_ver2_2',
        u'generic_android_ver2_3',
        u'generic_android_ver3_0',
        u'generic_android_ver3_1',
        u'generic_android_ver3_2',
        u'generic_android_ver3_3',
        u'generic_android_ver4',
        u'generic_android_ver4_1',

        u'uabait_opera_mini_android_v50',
        u'uabait_opera_mini_android_v51',
        u'generic_opera_mini_android_version5',

        u'generic_android_ver1_5_opera_mobi',
        u'generic_android_ver1_5_opera_mobi_11',
        u'generic_android_ver1_6_opera_mobi',
        u'generic_android_ver1_6_opera_mobi_11',
        u'generic_android_ver2_0_opera_mobi',
        u'generic_android_ver2_0_opera_mobi_11',
        u'generic_android_ver2_1_opera_mobi',
        u'generic_android_ver2_1_opera_mobi_11',
        u'generic_android_ver2_2_opera_mobi',
        u'generic_android_ver2_2_opera_mobi_11',
        u'generic_android_ver2_3_opera_mobi',
        u'generic_android_ver2_3_opera_mobi_11',
        u'generic_android_ver4_0_opera_mobi',
        u'generic_android_ver4_0_opera_mobi_11',

        u'generic_android_ver2_1_opera_tablet',
        u'generic_android_ver2_2_opera_tablet',
        u'generic_android_ver2_3_opera_tablet',
        u'generic_android_ver3_0_opera_tablet',
        u'generic_android_ver3_1_opera_tablet',
        u'generic_android_ver3_2_opera_tablet',

        u'generic_android_ver2_0_fennec',
        u'generic_android_ver2_0_fennec_tablet',
        u'generic_android_ver2_0_fennec_desktop',

        u'generic_android_ver1_6_ucweb',
        u'generic_android_ver2_0_ucweb',
        u'generic_android_ver2_1_ucweb',
        u'generic_android_ver2_2_ucweb',
        u'generic_android_ver2_3_ucweb',

        u'generic_android_ver2_0_netfrontlifebrowser',
        u'generic_android_ver2_1_netfrontlifebrowser',
        u'generic_android_ver2_2_netfrontlifebrowser',
        u'generic_android_ver2_3_netfrontlifebrowser',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Android')

    def apply_conclusive_match(self, ua):
        # Look for RIS delimited UAs first.
        delimiter_idx = ua.find(constants.RIS_DELIMITER)
        if delimiter_idx != -1:
            tolerance = delimiter_idx + len(constants.RIS_DELIMITER)
            return self.get_device_id_from_ris(ua, tolerance)

        # Opera Mini.
        if Utils.check_if_contains(ua, u'Opera Mini'):
            if Utils.check_if_contains(ua, u' Build/'):
                tolerance = Utils.index_of_or_length(ua, ' Build/')
                return self.get_device_id_from_ris(ua, tolerance)
            prefixes = OrderedDict([
                (u'Opera/9.80 (J2ME/MIDP; Opera Mini/5', u'uabait_opera_mini_android_v50'),
                (u'Opera/9.80 (Android; Opera Mini/5.0', u'uabait_opera_mini_android_v50'),
                (u'Opera/9.80 (Android; Opera Mini/5.1', u'uabait_opera_mini_android_v51'),
            ])
            for prefix, default_id in prefixes.iteritems():
                if Utils.check_if_starts_with(ua, prefix):
                    return self.get_device_id_from_ris(ua, len(prefix))

        # Opera Mobi.
        if Utils.check_if_contains(ua, u'Opera Mobi'):
            tolerance = Utils.second_slash(ua)
            return self.get_device_id_from_ris(ua, tolerance)

        # Opera Tablet.
        if Utils.check_if_contains(ua, u'Opera Tablet'):
            tolerance = Utils.second_slash(ua)
            return self.get_device_id_from_ris(ua, tolerance)

        # Fennec.
        if Utils.check_if_contains_any_of(ua, [u'Fennec', u'Firefox']):
            tolerance = Utils.index_of_or_length(ua, u')')
            return self.get_device_id_from_ris(ua, tolerance)

        # UCWEB7.
        if Utils.check_if_contains(ua, u'UCWEB7'):
            # The tolerance is after UCWEB7, not before.
            find = u'UCWEB7'
            find_index = ua.find(find)
            tolerance = (find_index if find_index != -1 else 0) + len(find)
            if tolerance > len(ua):
                tolerance = len(ua)
            return self.get_device_id_from_ris(ua, tolerance)

        # NetFrontLifeBrowser.
        if Utils.check_if_contains(ua, u'NetFrontLifeBrowser/2.2'):
            find = u'NetFrontLifeBrowser/2.2'
            find_index = ua.find(find)
            tolerance = (find_index if find_index != -1 else 0) + len(find)
            if tolerance > len(ua):
                tolerance = len(ua)
            return self.get_device_id_from_ris(ua, tolerance)

        # Standard RIS Matching.
        tolerance = min(
            Utils.index_of_or_length(ua, u' Build/'),
            Utils.index_of_or_length(ua, u' AppleWebKit'))
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        # Opera Mini.
        if Utils.check_if_contains(ua, u'Opera Mini'):
            return u'generic_opera_mini_android_version5'

        # Opera Mobi.
        if Utils.check_if_contains(ua, u'Opera Mobi'):
            android_version = self.get_android_version(ua) or u''
            opera_version = self.get_opera_on_android_version(ua) or u''
            # Convert versions (2.1) to device ID versions (2_1).
            android_version_string = android_version.replace(u'.', u'_')
            # Build initial device ID string.
            device_id = u'generic_android_ver' + android_version_string + u'_opera_mobi'
            # Opera Mobi 10 does not have a version in its WURFL ID (ex: generic_android_ver1_5_opera_mobi).
            if opera_version != '10':
                device_id = u'_' + opera_version
            # Device ID should look something like this at this point: generic_android_ver2_3_opera_mobi_11.
            # Now we must make sure the deviceID is valid.
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'generic_android_ver2_0_opera_mobi'

        # Opera Tablet.
        if Utils.check_if_contains(ua, u'Opera Tablet'):
            android_version = float(self.get_android_version(ua) or 0)
            if android_version < 2.1:
                android_version = 2.1
            elif android_version > 3.2:
                android_version = 3.2
            android_version_string = unicode(android_version).replace('u.', u'_')
            device_id = u'generic_android_ver' + android_version_string + u'_opera_tablet'
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'generic_android_ver2_1_opera_tablet'

        # UCWEB7.
        if Utils.check_if_contains(ua, u'UCWEB7'):
            android_version_string = (self.get_android_version(ua) or u'').replace(u'.', u'_')
            device_id = u'generic_android_ver' + android_version_string + u'_ucweb'
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'generic_android_ver2_0_ucweb'

        # Fennec.
        is_fennec = Utils.check_if_contains(ua, u'Fennec')
        is_firefox = Utils.check_if_contains(ua, u'Firefox')
        if is_fennec or is_firefox:
            if is_fennec or Utils.check_if_contains(ua, u'Mobile'):
                return u'generic_android_ver2_0_fennec'
            if is_firefox:
                if Utils.check_if_contains(ua, u'Tablet'):
                    return u'generic_android_ver2_0_fennec_tablet'
                if Utils.check_if_contains(ua, u'Desktop'):
                    return u'generic_android_ver2_0_fennec_desktop'
                return constants.NO_MATCH

        # NetFrontLifeBrowser.
        if Utils.check_if_contains(ua, u'NetFrontLifeBrowser'):
            # generic_android_ver2_0_netfrontlifebrowser.
            android_version_string = (self.get_android_version(ua) or u'').replace(u'.', u'_')
            device_id = u'generic_android_ver' + android_version_string + u'_netfrontlifebrowser'
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'generic_android_ver2_0_netfrontlifebrowser'

        # Generic Android.
        if Utils.check_if_contains(ua, u'Froyo'):
            return u'generic_android_ver2_2'
        version_string = (self.get_android_version(ua) or u'').replace(u'.', u'_')
        device_id = u'generic_android_ver' + version_string
        if device_id == u'generic_android_ver2_0':
            return u'generic_android_ver2'
        if device_id == u'generic_android_ver4_0':
            return u'generic_android_ver4'
        if device_id in self.constant_ids:
            return device_id

        return u'generic_android'

    ###########################################################################
    ## Android Utility Functions.
    ###########################################################################

    default_android_version = u'2.0'
    valid_android_versions = [u'1.0', u'1.5', u'1.6', u'2.0', u'2.1', u'2.2', u'2.3', u'2.4', u'3.0', u'3.1', u'3.2', u'3.3', u'4.0', u'4.1']
    android_release_map = OrderedDict([
        (u'Cupcake', u'1.5'),
        (u'Donut', u'1.6'),
        (u'Eclair', u'2.1'),
        (u'Froyo', u'2.2'),
        (u'Gingerbread', u'2.3'),
        (u'Honeycomb', u'3.0'),
        # (u'Ice Cream Sandwich', u'4.0'),
    ])

    @classmethod
    def get_android_version(cls, ua, use_default=True):
        # Replace Android version names with their numbers.
        # ex: Froyo => 2.2
        pattern = u'|'.join(map(re.escape, cls.android_release_map.keys()))
        ua = re.sub(pattern, lambda m: cls.android_release_map[m.group()], ua)
        matches = re.search(r'Android (\d\.\d)', ua)
        if matches is not None:
            version = matches.group(1)
            if version in cls.valid_android_versions:
                return version
        return cls.default_android_version if use_default else None

    default_opera_version = u'10'
    valid_opera_versions = [u'10', u'11']

    @classmethod
    def get_opera_on_android_version(cls, ua, use_default=True):
        matches = re.search(r'Version\/(\d\d)', ua)
        if matches is not None:
            version = matches.group(1)
            if version in cls.valid_opera_versions:
                return version
        return cls.default_opera_version if use_default else None

    @classmethod
    def get_android_model(cls, ua, use_default=True):
        matches = re.search(r'Android [^;]+; xx-xx; (.+?) Build/', ua)
        if matches is None:
            return None

        # Trim off spaces and semicolons.
        model = matches.group(1).rstrip(u' ;')
        # The previous RegEx may return just "Build/.*" for UAs like:
        # HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; xx-xx; Build/CUPCAKE) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1
        if model.find(u'Build/') == 0:
            return None

        # HTC.
        if model.find(u'HTC') != -1:
            # Normalize "HTC/".
            model = re.sub(r'HTC[ _\-/]', r'HTC~', model)
            # Remove the version.
            model = re.sub(r'(/| V?[\d\.]).*$', r'', model)
            model = re.sub(r'/.*$', r'', model)
        # Samsung.
        model = re.sub(r'(SAMSUNG[^/]+)/.*$', r'\1', model)
        # Orange.
        model = re.sub(r'ORANGE/.*$', r'ORANGE', model)
        # LG.
        model = re.sub(r'(LG-[^/]+)/[vV].*$', r'\1', model)
        # Serial Number.
        model = re.sub(r'\[[\d]{10}\]', r'', model)

        return model.strip()


class AppleHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_AppleHandler'.
    '''
    constant_ids = [
        u'apple_ipod_touch_ver1',
        u'apple_ipod_touch_ver2',
        u'apple_ipod_touch_ver3',
        u'apple_ipod_touch_ver4',
        u'apple_ipod_touch_ver5',

        u'apple_ipad_ver1',
        u'apple_ipad_ver1_sub42',
        u'apple_ipad_ver1_sub5',

        u'apple_iphone_ver1',
        u'apple_iphone_ver2',
        u'apple_iphone_ver3',
        u'apple_iphone_ver4',
        u'apple_iphone_ver5',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with(ua, u'Mozilla/5') and \
            Utils.check_if_contains_any_of(ua, [u'iPhone', u'iPod', u'iPad'])

    def apply_conclusive_match(self, ua):
        tolerance = ua.find(u'_')
        if tolerance != -1:
            # The first char after the first underscore.
            tolerance += 1
        else:
            index = ua.find(u'like Mac OS X;')
            if index != -1:
                # Step through the search string to the semicolon at the end.
                tolerance = index + 14
            else:
                # Non-typical UA, try full length match.
                tolerance = len(ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        matches = re.search(r' (\d)_(\d)[ _]', ua)
        if matches is not None:
            major_version = int(matches.group(1))
            minor_version = int(matches.group(2))
        else:
            major_version = -1
            minor_version = -1
        # Check iPods first since they also contain 'iPhone'.
        if Utils.check_if_contains(ua, u'iPod'):
            device_id = u'apple_ipod_touch_ver' + str(major_version)
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'apple_ipod_touch_ver1'
        elif Utils.check_if_contains(ua, u'iPad'):
            if major_version == 5:
                return u'apple_ipad_ver1_sub5'
            elif major_version == 4:
                return u'apple_ipad_ver1_sub42'
            else:
                return u'apple_ipad_ver1'
        elif Utils.check_if_contains(ua, u'iPhone'):
            device_id = u'apple_iphone_ver' + str(major_version)
            if device_id in self.constant_ids:
                return device_id
            else:
                return u'apple_iphone_ver1'
        return None


class BenQHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_BenQHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with(ua, u'BenQ') or \
            Utils.check_if_starts_with(ua, u'BENQ')


class BlackBerryHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_BlackBerryHandler'.
    '''
    constant_ids = OrderedDict([
        (u'2.', u'blackberry_generic_ver2'),
        (u'3.2', u'blackberry_generic_ver3_sub2'),
        (u'3.3', u'blackberry_generic_ver3_sub30'),
        (u'3.5', u'blackberry_generic_ver3_sub50'),
        (u'3.6', u'blackberry_generic_ver3_sub60'),
        (u'3.7', u'blackberry_generic_ver3_sub70'),
        (u'4.1', u'blackberry_generic_ver4_sub10'),
        (u'4.2', u'blackberry_generic_ver4_sub20'),
        (u'4.3', u'blackberry_generic_ver4_sub30'),
        (u'4.5', u'blackberry_generic_ver4_sub50'),
        (u'4.6', u'blackberry_generic_ver4_sub60'),
        (u'4.7', u'blackberry_generic_ver4_sub70'),
        (u'4.', u'blackberry_generic_ver4'),
        (u'5.', u'blackberry_generic_ver5'),
        (u'6.', u'blackberry_generic_ver6'),
    ])

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains_case_insensitive(ua, u'BlackBerry')

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with(ua, u'Mozilla/4'):
            tolerance = Utils.second_slash(ua)
        elif Utils.check_if_starts_with(ua, u'Mozilla/5'):
            tolerance = Utils.ordinal_index_of(ua, u';', 3)
        else:
            tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        # No need for case insensitivity here, BlackBerry was fixed in the normalizer.
        matches = re.search(r'BlackBerry[^/\s]+/(\d.\d)', ua)
        if matches is not None:
            version = matches.group(1)
            for vercode, device_id in self.constant_ids.iteritems():
                if version.find(vercode) != -1:
                    return device_id
        return None


class BotCrawlerTranscoderHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_BotCrawlerTranscoderHandler'.
    '''
    _bot_crawler_transcoder = [
        u'bot',
        u'crawler',
        u'spider',
        u'novarra',
        u'transcoder',
        u'yahoo! searchmonkey',
        u'yahoo! slurp',
        u'feedfetcher-google',
        u'toolbar',
        u'mowser',
        u'mediapartners-google',
        u'azureus',
        u'inquisitor',
        u'baiduspider',
        u'baidumobaider',
        u'holmes/',
        u'libwww-perl',
        u'netSprint',
        u'yandex',
        u'cfnetwork',
        u'ineturl',
        u'jakarta',
        u'lorkyll',
        u'microsoft url control',
        u'indy library',
        u'slurp',
        u'crawl',
        u'wget',
        u'ucweblient',
        u'rma',
        u'snoopy',
        u'untrursted',
        u'mozfdsilla',
        u'ask jeeves',
        u'jeeves/teoma',
        u'mechanize',
        u'http client',
        u'servicemonitor',
        u'httpunit',
        u'hatena',
        u'ichiro'
    ]

    def can_handle(self, ua):
        for key in self._bot_crawler_transcoder:
            if Utils.check_if_contains_case_insensitive(ua, key):
                return True
        return False


class CatchAllHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_CatchAllHandler'.
    '''
    MOZILLA_TOLERANCE = 5

    MOZILLA5 = u'CATCH_ALL_MOZILLA5'
    MOZILLA4 = u'CATCH_ALL_MOZILLA4'

    def __init__(self, *args, **kwargs):
        super(CatchAllHandler, self).__init__(*args, **kwargs)
        self._mozilla4_uas_with_device_id = {}
        self._mozilla4_ordered_uas = None
        self._mozilla5_uas_with_device_id = {}
        self._mozilla5_ordered_uas = None

    def can_handle(self, ua):
        return True

    def apply_conclusive_match(self, ua):
        device_id = constants.GENERIC
        if Utils.check_if_starts_with(ua, u'Mozilla'):
            device_id = self._apply_mozilla_conclusive_match(ua)
        else:
            tolerance = Utils.first_slash(ua)
            device_id = self.get_device_id_from_ris(ua, tolerance)
        return device_id

    def apply_exact_match(self, ua):
        if ua in self._uas_with_device_id:
            return self._uas_with_device_id[ua]
        if ua in self._mozilla4_uas_with_device_id:
            return self._mozilla4_uas_with_device_id[ua]
        if ua in self._mozilla5_uas_with_device_id:
            return self._mozilla5_uas_with_device_id[ua]
        return constants.NO_MATCH

    def _apply_mozilla_conclusive_match(self, ua):
        if self._is_mozilla5(ua):
            return self._apply_mozilla5_conclusive_match(ua)
        if self._is_mozilla4(ua):
            return self._apply_mozilla4_conclusive_match(ua)
        match = Utils.ld_match(self._get_ordered_uas(), ua, self.MOZILLA_TOLERANCE)
        return self._uas_with_device_id[match]

    def _apply_mozilla5_conclusive_match(self, ua):
        if ua not in self._mozilla5_uas_with_device_id:
            match = Utils.ld_match(self._get_mozilla5_ordered_uas(), ua, self.MOZILLA_TOLERANCE)
        if match:
            return self._mozilla5_uas_with_device_id[match]
        return constants.NO_MATCH

    def _apply_mozilla4_conclusive_match(self, ua):
        if ua not in self._mozilla4_uas_with_device_id:
            match = Utils.ld_match(self._get_mozilla4_ordered_uas(), ua, self.MOZILLA_TOLERANCE)
        if match:
            return self._mozilla4_uas_with_device_id[match]
        return constants.NO_MATCH

    def filter(self, ua, device_id):
        if self._is_mozilla4(ua):
            self._mozilla4_uas_with_device_id[self._normalizer.normalize(ua)] = device_id
            self._mozilla4_ordered_uas = None
        if self._is_mozilla5(ua):
            self._mozilla5_uas_with_device_id[self._normalizer.normalize(ua)] = device_id
            self._mozilla5_ordered_uas = None
        super(CatchAllHandler, self).filter(ua, device_id)

    def _is_mozilla5(self, ua):
        return Utils.check_if_starts_with(ua, 'Mozilla/5')

    def _is_mozilla4(self, ua):
        return Utils.check_if_starts_with(ua, 'Mozilla/4')

    def _is_mozilla(self, ua):
        return Utils.check_if_starts_with(ua, u'Mozilla')

    def _get_mozilla4_ordered_uas(self):
        if self._mozilla4_ordered_uas is None:
            self._mozilla4_ordered_uas = self._mozilla4_uas_with_device_id.keys()
            self._mozilla4_ordered_uas.sort()
        return self._mozilla4_ordered_uas

    def _get_mozilla5_ordered_uas(self):
        if self._mozilla5_ordered_uas is None:
            self._mozilla5_ordered_uas = self._mozilla5_uas_with_device_id.keys()
            self._mozilla5_ordered_uas.sort()
        return self._mozilla5_ordered_uas


class ChromeHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_ChromeHandler'.
    '''
    constant_ids = [
        u'google_chrome',
    ]

    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Chrome')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.index_of_or_length(u'/', ua, ua.find(u'Chrome'))
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        return u'google_chrome'


class DoCoMoHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_DoCoMoHandler'.
    '''
    constant_ids = [
        u'docomo_generic_jap_ver1',
        u'docomo_generic_jap_ver2',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'DoCoMo')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.ordinal_index_of(ua, u'/', 2)
        if tolerance == -1:
            # DoCoMo/2.0 F01A(c100;TB;W24H17)
            tolerance = Utils.index_of_or_length(u'(', ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        version_index = 7
        version = ua[version_index]
        return u'docomo_generic_jap_ver2' if version == '2' else u'docomo_generic_jap_ver1'


class FirefoxHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_FirefoxHandler'.
    '''
    constant_ids = [
        u'firefox',
        u'firefox_1',
        u'firefox_2',
        u'firefox_3',
        u'firefox_4_0',
        u'firefox_5_0',
        u'firefox_6_0',
        u'firefox_7_0',
        u'firefox_8_0',
        u'firefox_9_0',
        u'firefox_10_0',
        u'firefox_11_0',
        u'firefox_12_0',
    ]

    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        if Utils.check_if_contains_any_of(ua, [u'Tablet', u'Sony', u'Novarra', u'Opera']):
            return False
        return Utils.check_if_contains(ua, u'Firefox')

    def apply_conclusive_match(self, ua):
        return self.get_device_id_from_ris(ua, Utils.index_of_or_length(ua, u'.'))

    def apply_recovery_match(self, ua):
        matches = re.search(r'Firefox\/(\d+)\.\d', ua)
        if matches is not None:
            firefox_version = matches.group(1)
            if int(firefox_version) <= 3:
                id = u'firefox_' + firefox_version
            else:
                id = u'firefox_' + firefox_version + '_0'
            if id in self.constant_ids:
                return id
        return u'firefox'


class GrundigHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_GrundigHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'Grundig', u'GRUNDIG'])


class HTCHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_HTCHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains_any_of(ua, [u'HTC', u'XV6875'])


class HTCMacHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_HTCMacHandler'.
    '''
    constant_ids = [
        u'generic_android_htc_disguised_as_mac',
    ]

    def can_handle(self, ua):
        return \
            Utils.check_if_starts_with(ua, u'Mozilla/5.0 (Macintosh') and \
            Utils.check_if_contains(ua, u'HTC')

    def apply_conclusive_match(self, ua):
        delimiter_idx = ua.find(constants.RIS_DELIMITER)
        if delimiter_idx != -1:
            tolerance = delimiter_idx + len(constants.RIS_DELIMITER)
            return self.get_device_id_from_ris(ua, tolerance)
        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        return u'generic_android_htc_disguised_as_mac'

    @classmethod
    def get_htcmac_model(cls, ua):
        matches = re.search(r'(HTC[^;\)]+)', ua)
        if matches is not None:
            model = re.sub(r'[ _\-/]', r'~', matches.group(1))
            return model
        return None


class JavaMidletHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_JavaMidletHandler'.
    '''
    constant_ids = [
        u'generic_midp_midlet',
    ]

    def can_handle(self, ua):
        return Utils.check_if_contains(ua, u'UNTRUSTED/1.0')

    def apply_conclusive_match(self, ua):
        return u'generic_midp_midlet'


class KDDIHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_KDDIHandler'.
    '''
    constant_ids = [
        u'opwv_v62_generic',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'KDDI-')

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with(ua, u'KDDI/'):
            tolerance = Utils.second_slash(ua)
        else:
            tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        return u'opwv_v62_generic'


class KindleHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_KindleHandler'.
    '''
    constant_ids = [
        u'amazon_kindle_ver1',
        u'amazon_kindle2_ver1',
        u'amazon_kindle3_ver1',
        u'amazon_kindle_fire_ver1',
        u'generic_amazon_android_kindle',
        u'generic_amazon_kindle',
    ]

    def can_handle(self, ua):
        return Utils.check_if_contains_any_of(ua, [u'Kindle', u'Silk'])

    def apply_conclusive_match(self, ua):
        search = u'Kindle/'
        idx = ua.find(search)
        if idx != -1:
            # Version/4.0 Kindle/3.0 (screen 600x800; rotate) Mozilla/5.0 (Linux; U; zh-cn.utf8) AppleWebKit/528.5+ (KHTML, like Gecko, Safari/528.5+)
            #		$idx ^	  ^ $tolerance
            tolerance = idx + len(search) + 1
            kindle_version = ua[tolerance]
            # RIS match only Kindle/1-3
            if kindle_version >= 1 and kindle_version <= 3:
                return self.get_device_id_from_ris(ua, tolerance)

        delimiter_idx = ua.find(constants.RIS_DELIMITER)
        if delimiter_idx != -1:
            tolerance = delimiter_idx + len(constants.RIS_DELIMITER)
            return self.get_device_id_from_ris(ua, tolerance)

        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'Kindle/1'):
            return u'amazon_kindle_ver1'
        if Utils.check_if_contains(ua, u'Kindle/2'):
            return u'amazon_kindle2_ver1'
        if Utils.check_if_contains(ua, u'Kindle/3'):
            return u'amazon_kindle3_ver1'
        if Utils.check_if_contains_any_of(ua, [u'Kindle Fire', u'Silk']):
            return u'amazon_kindle_fire_ver1'
        return u'generic_amazon_kindle'


class KonquerorHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_KonquerorHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Konqueror')


class KyoceraHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_KyoceraHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'kyocera', u'QC-', u'KWC-'])


class LGHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_LGHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'lg', u'LG'])

    def apply_conclusive_match(self, ua):
        tolerance = Utils.index_of_or_length(ua, u'/', ua.upper().find(u'LG'))
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        return self.get_device_id_from_ris(ua, 7)


class LGUPLUSHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_LGUPLUSHandler'.
    '''
    constant_ids = [
        u'generic_lguplus_rexos_facebook_browser',
        u'generic_lguplus_rexos_webviewer_browser',
        u'generic_lguplus_winmo_facebook_browser',
        u'generic_lguplus_android_webkit_browser',
    ]

    lgupluses = OrderedDict([
        (u'generic_lguplus_rexos_facebook_browser', [
            u'Windows NT 5',
            u'POLARIS',
        ]),
        (u'generic_lguplus_rexos_webviewer_browser', [
            u'Windows NT 5',
        ]),
        (u'generic_lguplus_winmo_facebook_browser', [
            u'Windows CE',
            u'POLARIS',
        ]),
        (u'generic_lguplus_android_webkit_browser', [
            u'Android',
            u'AppleWebKit',
        ]),
    ])

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains_any_of(ua, [u'LGUPLUS', u'lgtelecom'])

    def apply_conclusive_match(self, ua):
        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        for device_id, values in self.lgupluses.iteritems():
            if Utils.check_if_contains_all(ua, values):
                return device_id
        return None


class MSIEHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_MSIEHandler'.
    '''
    constant_ids = [
        u'msie',
        u'msie_4',
        u'msie_5',
        u'msie_5_5',
        u'msie_6',
        u'msie_7',
        u'msie_8',
        u'msie_9',
    ]

    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        if Utils.check_if_contains_any_of(ua, [u'Opera', u'armv', u'MOTO', u'BREW']):
            return False
        return \
            Utils.check_if_starts_with(ua, u'Mozilla') and \
            Utils.check_if_contains(ua, u'MSIE')

    def apply_conclusive_match(self, ua):
        matches = re.search(r'^Mozilla\/4\.0 \(compatible; MSIE (\d)\.(\d);', ua)
        if matches is not None:
            value = int(matches.group(1))
            # Cases are intentionally out of sequence for performance.
            if value == 7:
                return u'msie_7'
            elif value == 8:
                return u'msie_8'
            elif value == 9:
                return u'msie_9'
            elif value == 6:
                return u'msie_6'
            elif value == 4:
                return u'msie_4'
            elif value == 5:
                return u'msie_5_5' if int(matches.group(2)) == 5 else u'msie_5'
            else:
                return u'msie'
        tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class MitsubishiHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_MitsubishiHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'Mitsu')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.first_space(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class MotorolaHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_MotorolaHandler'.
    '''
    constant_ids = [
        u'mot_mib22_generic',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with_any_of(ua, [u'Mot-', u'MOT-', u'MOTO', u'moto']) or \
            Utils.check_if_contains(ua, u'Motorola')

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with_any_of(ua, [u'Mot-', u'MOT-', u'Motorola']):
            return self.get_device_id_from_ris(ua, Utils.first_slash(ua))
        return self.get_device_id_from_ld(ua, 5)

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains_any_of(ua, [u'MIB/2.2', u'MIB/BER2.2']):
            return u'mot_mib22_generic'
        return None


class NecHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_NecHandler'.
    '''
    NEC_KGT_TOLERANCE = 2

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'NEC-', u'KGT'])

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with(ua, u'NEC-'):
            tolerance = Utils.first_slash(ua)
            return self.get_device_id_from_ris(ua, tolerance)
        return self.get_device_id_from_ld(ua, self.NEC_KGT_TOLERANCE)


class NintendoHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_NintendoHandler'.
    '''
    constant_ids = [
        u'nintendo_wii_ver1',
        u'nintendo_dsi_ver1',
        u'nintendo_ds_ver1',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        if Utils.check_if_contains(ua, u'Nintendo'):
            return True
        return \
            Utils.check_if_starts_with(ua, u'Mozilla/') and \
            Utils.check_if_contains_all(ua, [u'Nitro', u'Opera'])

    def apply_conclusive_match(self, ua):
        return self.get_device_id_from_ld(ua)

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'Nintendo Wii'):
            return u'nintendo_wii_ver1'
        if Utils.check_if_contains(ua, u'Nintendo DSi'):
            return u'nintendo_dsi_ver1'
        if Utils.check_if_starts_with(ua, u'Mozilla/') and Utils.check_if_contains_all(ua, [u'Nitro', u'Opera']):
            return u'nintendo_ds_ver1'
        return u'nintendo_wii_ver1'


class NokiaHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_NokiaHandler'.
    '''
    constant_ids = [
        u'nokia_generic_series60',
        u'nokia_generic_series80',
        u'nokia_generic_meego',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Nokia')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.index_of_any_or_length(ua, [u'/', u' '], ua.find(u'Nokia'))
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'Series60'):
            return u'nokia_generic_series60'
        if Utils.check_if_contains(ua, u'Series80'):
            return u'nokia_generic_series80'
        if Utils.check_if_contains(ua, u'MeeGo'):
            return u'nokia_generic_meego'
        return None


class NokiaOviBrowserHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_NokiaOviBrowserHandler'.
    '''
    constant_ids = [
        u'nokia_generic_series40_ovibrosr',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'S40OviBrowser')

    def apply_conclusive_match(self, ua):
        idx = ua.find('Nokia')
        if idx == -1:
            return constants.NO_MATCH
        tolerance = Utils.index_of_any_or_length(ua, [u'/', u' '], idx)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        return u'nokia_generic_series40_ovibrosr'


class OperaHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_OperaHandler'.
    '''
    constant_ids = [
        u'opera',
        u'opera_7',
        u'opera_8',
        u'opera_9',
        u'opera_10',
        u'opera_11',
        u'opera_12',
    ]

    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Opera')

    def apply_conclusive_match(self, ua):
        opera_idx = ua.find(u'Opera')
        tolerance = Utils.index_of_or_length(ua, u'.', opera_idx)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        opera_version = self.get_opera_version(ua)
        if opera_version is None:
            return u'opera'
        major_version = math.floor(float(opera_version))
        id = u'opera_' + str(major_version)
        if id in self.constant_ids:
            return id
        return u'opera'

    @classmethod
    def get_opera_version(cls, ua):
        matches = re.search(r'Opera[ /]?(\d+\.\d+)', ua)
        if matches is not None:
            return matches.group(1)
        return None


class OperaMiniHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_OperaMiniHandler'.
    '''
    _opera_minis = OrderedDict([
        (u'Opera Mini/1', u'generic_opera_mini_version1'),
        (u'Opera Mini/2', u'generic_opera_mini_version2'),
        (u'Opera Mini/3', u'generic_opera_mini_version3'),
        (u'Opera Mini/4', u'generic_opera_mini_version4'),
        (u'Opera Mini/5', u'generic_opera_mini_version5'),
    ])

    def can_handle(self, ua):
        return Utils.check_if_contains(ua, u'Opera Mini')

    def apply_recovery_match(self, ua):
        for key, device_id in self._opera_minis:
            if Utils.check_if_contains(ua, key):
                return device_id
        if Utils.check_if_contains(ua, u'Opera Mobi'):
            return u'generic_opera_mini_version4'
        return u'generic_opera_mini_version1'


class PanasonicHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_PanasonicHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'Panasonic')


class PantechHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_PantechHandler'.
    '''
    PANTECH_TOLERANCE = 5

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'Pantech', u'PT-', u'PANTECH', u'PG-'])

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with(ua, u'Pantech'):
            tolerance = self.PANTECH_TOLERANCE
        else:
            tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class PhilipsHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_PhilipsHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with(ua, u'Philips') or \
            Utils.check_if_starts_with(ua, u'PHILIPS')


class PortalmmmHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_PortalmmmHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'portalmmm')

    def apply_conclusive_match(self, ua):
        return constants.NO_MATCH


class QtekHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_QtekHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'Qtek')


class ReksioHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_ReksioHandler'.
    '''
    constant_ids = [
        'generic_reksio',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, 'Reksio')

    def apply_conclusive_match(self, ua):
        return u'generic_reksio'


class SPVHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SPVHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'SPV')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.index_of_or_length(ua, u';', ua.find(u'SPV'))
        return self.get_device_id_from_ris(ua, tolerance)


class SafariHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SafariHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_mobile_browser(ua):
            return False
        return \
            Utils.check_if_starts_with(ua, u'Mozilla') and \
            Utils.check_if_contains(ua, u'Safari')


class SagemHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SagemHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'Sagem', u'SAGEM'])


class SamsungHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SamsungHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_contains_any_of(ua, [u'Samsung', u'SAMSUNG']) or \
            Utils.check_if_starts_with_any_of(ua, [u'SEC-', u'SPH', u'SGH', u'SCH'])

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with_any_of(ua, [u'SEC-', u'SAMSUNG-', u'SCH']):
            tolerance = Utils.first_slash(ua)
        elif Utils.check_if_starts_with_any_of(ua, [u'Samsung', u'SPH', u'SGH']):
            tolerance = Utils.first_space(ua)
        else:
            tolerance = Utils.second_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        if Utils.check_if_starts_with(ua, u'SAMSUNG'):
            tolerance = 8
            return self.get_device_id_from_ld(ua, tolerance)
        else:
            index = ua.find(u'Samsung')
            tolerance = Utils.index_of_or_length(ua, u'/', index if index != -1 else 0)
            return self.get_device_id_from_ris(ua, tolerance)


class SanyoHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SanyoHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return \
            Utils.check_if_starts_with_any_of(ua, [u'Sanyo', u'SANYO']) or \
            Utils.check_if_contains(ua, u'MobilePhone')

    def apply_conclusive_match(self, ua):
        idx = ua.find(u'MobilePhone')
        if idx != -1:
            tolerance = Utils.index_of_or_length(u'/', ua, idx)
        else:
            tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class SharpHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SharpHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with_any_of(ua, [u'Sharp', u'SHARP'])


class SiemensHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SiemensHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'SIE-')


class SmartTVHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SmartTVHandler'.
    '''
    constant_ids = [
        u'generic_smarttv_browser',
        u'generic_smarttv_googletv_browser',
        u'generic_smarttv_appletv_browser',
        u'generic_smarttv_boxeebox_browser',
    ]

    def can_handle(self, ua):
        return Utils.is_smart_tv(ua)

    def apply_conclusive_match(self, ua):
        tolerance = len(ua)
        return self.get_device_id_from_ris(ua, tolerance)

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'SmartTV'):
            return u'generic_smarttv_browser'
        if Utils.check_if_contains(ua, u'GoogleTV'):
            return u'generic_smarttv_googletv_browser'
        if Utils.check_if_contains(ua, u'AppleTV'):
            return u'generic_smarttv_appletv_browser'
        if Utils.check_if_contains(ua, u'Boxee'):
            return u'generic_smarttv_boxeebox_browser'
        return u'generic_smarttv_browser'


class SonyEricssonHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_SonyEricssonHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Sony')

    def apply_conclusive_match(self, ua):
        if Utils.check_if_starts_with(ua, u'SonyEricsson'):
            tolerance = Utils.first_slash(ua) - 1
            return self.get_device_id_from_ris(ua, tolerance)
        tolerance = Utils.second_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class ToshibaHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_ToshibaHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'Toshiba')


class VodafoneHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_VodafoneHandler'.
    '''
    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_starts_with(ua, u'Vodafone')

    def apply_conclusive_match(self, ua):
        tolerance = Utils.first_slash(ua)
        return self.get_device_id_from_ris(ua, tolerance)


class WebOSHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_WebOSHandler'.
    '''
    constant_ids = [
        u'hp_tablet_webos_generic',
        u'hp_webos_generic',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains_any_of(ua, [u'webOS', u'hpwOS'])

    def apply_conclusive_match(self, ua):
        delimiter_idx = ua.find(constants.RIS_DELIMITER)
        if delimiter_idx != -1:
            tolerance = delimiter_idx + len(constants.RIS_DELIMITER)
            return self.get_device_id_from_ris(ua, tolerance)
        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        return u'hp_tablet_webos_generic' if Utils.check_if_contains(ua, u'hpwOS/3') else u'hp_webos_generic'

    @classmethod
    def get_webos_model_version(cls, ua):
        # Formats:
        #   Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.5; U; es-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.83 Safari/534.6 TouchPad/1.0
        #   Mozilla/5.0 (Linux; webOS/2.2.4; U; de-DE) AppleWebKit/534.6 (KHTML, like Gecko) webOSBrowser/221.56 Safari/534.6 Pre/3.0
        #   Mozilla/5.0 (webOS/1.4.0; U; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Version/1.0 Safari/532.2 Pre/1.0
        matches = re.search(r' ([^/]+)/([\d\.]+)$', ua)
        if matches is not None:
            return matches.group(1) + ' ' + matches.group(2)
        else:
            return None

    @classmethod
    def get_webos_version(cls, ua):
        matches = re.search(r'(?:hpw|web)OS.(\d)\.', ua)
        if matches is not None:
            return u'webOS' + matches.group(1)
        else:
            return None


class WindowsPhoneDesktopHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_WindowsPhoneDesktopHandler'.
    '''
    constant_ids = [
        u'generic_ms_phone_os7_desktopmode',
        u'generic_ms_phone_os7_5_desktopmode',
    ]

    def can_handle(self, ua):
        return Utils.check_if_contains(ua, u'ZuneWP7')

    def apply_conclusive_match(self, ua):
        # Exact and Recovery match only.
        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'Trident/5.0'):
            return u'generic_ms_phone_os7_5_desktopmode'
        return u'generic_ms_phone_os7_desktopmode'


class WindowsPhoneHandler(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_WindowsPhoneHandler'.
    '''
    constant_ids = [
        u'generic_ms_winmo6_5',
        u'generic_ms_phone_os7',
        u'generic_ms_phone_os7_5',
    ]

    def can_handle(self, ua):
        if Utils.is_desktop_browser(ua):
            return False
        return Utils.check_if_contains(ua, u'Windows Phone')

    def apply_conclusive_match(self, ua):
        # Exact and Recovery match only.
        return constants.NO_MATCH

    def apply_recovery_match(self, ua):
        if Utils.check_if_contains(ua, u'Windows Phone 6.5'):
            return u'generic_ms_winmo6_5'
        if Utils.check_if_contains(ua, u'Windows Phone OS 7.0'):
            return u'generic_ms_phone_os7'
        if Utils.check_if_contains(ua, u'Windows Phone OS 7.5'):
            return u'generic_ms_phone_os7_5'
        return constants.NO_MATCH


class Utils(Handler):
    '''
    @see WURFL PHP 'WURFL_Handlers_Utils'.
    '''
    _mobile_browsers = [
        u'midp',
        u'mobile',
        u'android',
        u'samsung',
        u'nokia',
        u'up.browser',
        u'phone',
        u'opera mini',
        u'opera mobi',
        u'brew',
        u'sonyericsson',
        u'blackberry',
        u'netfront',
        u'uc browser',
        u'symbian',
        u'j2me',
        u'wap2.',
        u'up.link',
        u'windows ce',
        u'vodafone',
        u'ucweb',
        u'zte-',
        u'ipad;',
        u'docomo',
        u'armv',
        u'maemo',
        u'palm',
        u'bolt',
        u'fennec',
        u'wireless',
        u'adr-',
        # Required for HPM Safari.
        u'htc',
        u'nintendo',
        # These keywords keep IE-like mobile UAs out of the MSIE bucket.
        # ex: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; XBLWP7;  ZuneWP7)
        u'zunewp7',
        u'skyfire',
        u'silk',
        u'untrusted',
        u'lgtelecom',
        u' gt-',
        u'ventana',
    ]

    _smart_tv_browsers = [
        u'googletv',
        u'boxee',
        u'sonydtv',
        u'appletv',
        u'smarttv',
        u'dlna',
        u'netcast.tv',
    ]

    _desktop_browsers = [
        u'wow64',
        u'.net clr',
        u'gtb7',
        u'macintosh',
        u'slcc1',
        u'gtb6',
        u'funwebproducts',
        u'aol 9.',
        u'gtb8',
    ]

    _mobile_atch_all_ids = OrderedDict([
        # Openwave.
        (u'UP.Browser/7.2', u'opwv_v72_generic'),
        (u'UP.Browser/7', u'opwv_v7_generic'),
        (u'UP.Browser/6.2', u'opwv_v62_generic'),
        (u'UP.Browser/6', u'opwv_v6_generic'),
        (u'UP.Browser/5', u'upgui_generic'),
        (u'UP.Browser/4', u'uptext_generic'),
        (u'UP.Browser/3', u'uptext_generic'),

        # Series 60.
        (u'Series60', u'nokia_generic_series60'),

        # Access/Net Front.
        (u'NetFront/3.0', u'generic_netfront_ver3'),
        (u'ACS-NF/3.0', u'generic_netfront_ver3'),
        (u'NetFront/3.1', u'generic_netfront_ver3_1'),
        (u'ACS-NF/3.1', u'generic_netfront_ver3_1'),
        (u'NetFront/3.2', u'generic_netfront_ver3_2'),
        (u'ACS-NF/3.2', u'generic_netfront_ver3_2'),
        (u'NetFront/3.3', u'generic_netfront_ver3_3'),
        (u'ACS-NF/3.3', u'generic_netfront_ver3_3'),
        (u'NetFront/3.4', u'generic_netfront_ver3_4'),
        (u'NetFront/3.5', u'generic_netfront_ver3_5'),
        (u'NetFront/4.0', u'generic_netfront_ver4_0'),
        (u'NetFront/4.1', u'generic_netfront_ver4_1'),

        # CoreMedia.
        (u'CoreMedia', u'apple_iphone_coremedia_ver1'),

        # Windows CE.
        (u'Windows CE', u'generic_ms_mobile'),

        # Generic XHTML.
        (u'Obigo', constants.GENERIC_XHTML),
        (u'AU-MIC/2', constants.GENERIC_XHTML),
        (u'AU-MIC-', constants.GENERIC_XHTML),
        (u'AU-OBIGO/', constants.GENERIC_XHTML),
        (u'Teleca Q03B1', constants.GENERIC_XHTML),

        # Opera Mini.
        (u'Opera Mini/1', u'generic_opera_mini_version1'),
        (u'Opera Mini/2', u'generic_opera_mini_version2'),
        (u'Opera Mini/3', u'generic_opera_mini_version3'),
        (u'Opera Mini/4', u'generic_opera_mini_version4'),
        (u'Opera Mini/5', u'generic_opera_mini_version5'),

        # DoCoMo.
        (u'DoCoMo', u'docomo_generic_jap_ver1'),
        (u'KDDI', u'docomo_generic_jap_ver1'),
    ])

    @classmethod
    def ris_match(cls, collection, needle, tolerance):
        return RISMatcher.INSTANCE().match(collection, needle, tolerance)

    @classmethod
    def ld_match(cls, collection, needle, tolerance=7):
        return LDMatcher.INSTANCE().match(collection, needle, tolerance)

    @classmethod
    def index_of_or_length(cls, string, target, starting_index=0):
        length = len(string)
        pos = string.find(target, starting_index)
        return length if pos == -1 else pos

    @classmethod
    def index_of_any_or_length(cls, ua, needles, start_index):
        positions = []
        for needle in needles:
            pos = ua.find(needle, start_index)
            if pos != -1:
                positions.append(pos)
        positions.sort()
        return positions[0] if len(positions) > 0 else len(ua)

    @classmethod
    def reset(cls):
        cls._is_desktop_browser = None
        cls._is_mobile_browser = None
        cls._is_smart_tv = None

    @classmethod
    def is_mobile_browser(cls, ua):
        if cls._is_mobile_browser is not None:
            return cls._is_mobile_browser
        cls._is_mobile_browser = False
        ua = ua.lower()
        for key in cls._mobile_browsers:
            if ua.find(key) != -1:
                cls._is_mobile_browser = True
                break
        return cls._is_mobile_browser

    @classmethod
    def is_desktop_browser(cls, ua):
        if cls._is_desktop_browser is not None:
            return cls._is_desktop_browser
        cls._is_desktop_browser = False
        ua = ua.lower()
        for key in cls._desktop_browsers:
            if ua.find(key) != -1:
                cls._is_desktop_browser = True
                break
        return cls._is_desktop_browser

    @classmethod
    def get_mobile_catch_all_id(cls, ua):
        for key, device_id in cls._mobile_atch_all_ids.iteritems():
            if ua.find(key) != -1:
                return device_id
        return constants.NO_MATCH

    @classmethod
    def is_desktop_browser_heavy_duty_analysis(cls, ua):
        # Check Smart TV keywords.
        if Utils.is_smart_tv(ua):
            return False

        # Chrome.
        if Utils.check_if_contains(ua, u'Chrome') and not Utils.check_if_contains(ua, u'Ventana'):
            return True

        # Check mobile keywords.
        if Utils.is_mobile_browser(ua):
            return False

        if Utils.check_if_contains(ua, u'PPC'):
            return False  # PowerPC; not always mobile, but we'll kick it out.

        # Firefox;  fennec is already handled in the WurflConstants::$MOBILE_BROWSERS keywords.
        if Utils.check_if_contains(ua, u'Firefox') and not Utils.check_if_contains(ua, u'Tablet'):
            return True

        # Safari.
        matches = re.search(r'^Mozilla/5\.0 \((?:Macintosh|Windows)[^\)]+\) AppleWebKit/[\d\.]+ \(KHTML, like Gecko\) Version/[\d\.]+ Safari/[\d\.]+$', ua)
        if matches is not None:
            return True

        # Opera Desktop.
        if Utils.check_if_starts_with(ua, u"Opera/9.80 (Windows NT', 'Opera/9.80 (Macintosh"):
            return True

        # Check desktop keywords.
        if Utils.is_desktop_browser(ua):
            return True

        # Internet Explorer 9.
        matches = re.search(r'^Mozilla\/5\.0 \(compatible; MSIE 9\.0; Windows NT \d\.\d', ua)
        if matches is not None:
            return True

        # Internet Explorer <9.
        matches = re.search(r'^Mozilla\/4\.0 \(compatible; MSIE \d\.\d; Windows NT \d\.\d', ua)
        if matches is not None:
            return True

        return False

    @classmethod
    def is_smart_tv(cls, ua):
        if cls._is_smart_tv is not None:
            return cls._is_smart_tv
        cls._is_smart_tv = False
        ua = ua.lower()
        for key in cls._smart_tv_browsers:
            if ua.find(key) != -1:
                cls._is_smart_tv = True
                break
        return cls._is_smart_tv

    @classmethod
    def ordinal_index_of(cls, haystack, needle, ordinal):
        found = 0
        index = -1
        while True:
            index = haystack.find(needle, index + 1)
            if index < 0:
                return index
            found += 1
            if found >= ordinal:
                break
        return index

    @classmethod
    def first_slash(cls, string):
        first_slash = string.find(u'/')
        return first_slash if first_slash != -1 else len(string)

    @classmethod
    def second_slash(cls, string):
        first_slash = string.find(u'/')
        if first_slash == -1:
            return len(string)
        second_slash = string[first_slash+1:].find(u'/')
        return first_slash + second_slash if second_slash != -1 else first_slash

    @classmethod
    def first_space(cls, string):
        first_space = string.find(u' ')
        return first_space if first_space != -1 else len(string)

    @classmethod
    def check_if_contains(cls, haystack, needle):
        return haystack.find(needle) != -1

    @classmethod
    def check_if_contains_any_of(cls, haystack, needles=[]):
        for needle in needles:
            if cls.check_if_contains(haystack, needle):
                return True
        return False

    @classmethod
    def check_if_contains_all(cls, haystack, needles=[]):
        for needle in needles:
            if not cls.check_if_contains(haystack, needle):
                return False
        return True

    @classmethod
    def check_if_contains_case_insensitive(cls, haystack, needle):
        return haystack.upper().find(needle.upper()) != -1

    @classmethod
    def check_if_starts_with(cls, haystack, needle):
        return haystack.startswith(needle)

    @classmethod
    def check_if_starts_with_any_of(cls, haystack, needles):
        if isinstance(needles, list):
            for needle in needles:
                if haystack.startswith(needle):
                    return True
        return False

    @classmethod
    def remove_locale(cls, ua):
        return re.sub(r'; ?[a-z]{2}(?:-[a-zA-Z]{2})?(?:\.utf8|\.big5)?\b-?', r'; xx-xx', ua)
