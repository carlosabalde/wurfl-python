# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from wurfl_python import normalizers
from wurfl_python.normalizers import generic
from wurfl_python.normalizers import specific
from wurfl_python import handlers
from wurfl_python.exceptions import UnregisteredParentDeviceException

_chain = handlers.Chain()


def match(ua):
    '''
    Returns a Device class based on the provided user agent using the
    WURFL PHP 'accuracy' matching mode.
    @see WURFL PHP 'WURFL_UserAgentHandlerChain'.
    '''
    return Repository.find(_chain.match(unicode(ua)))


def find(id):
    '''
    Return a Device class linked to the provided WURFL device id. Returns
    None if it does not exist.
    '''
    return Repository.find(id)


class Repository(object):
    _DEVICES = {}

    class AbstractDevice(object):
        pass

    @classmethod
    def register(cls, id, ua, actual_device_root, capabilities={}, parent=None):
        if parent is None:
            class Device(cls.AbstractDevice):
                pass
        elif parent in cls._DEVICES:
            parent = cls._DEVICES[parent]

            class Device(parent):
                pass

            parent.children.add(Device)
        else:
            raise UnregisteredParentDeviceException()

        Device.id = id
        Device.ua = ua
        Device.actual_device_root = actual_device_root
        for name, value in capabilities.iteritems():
            setattr(Device, name, value)
        Device.parent = parent
        Device.children = set()

        cls._DEVICES[Device.id] = Device
        _chain.filter(Device.ua, Device.id)

    @classmethod
    def find(cls, id):
        return cls._DEVICES.get(id, None)


def _init():
    '''
    @see WURFL PHP 'WURFL_UserAgentHandlerChainFactory'.
    '''
    generic_normalizers = _create_generic_normalizers()

    # Java Midlets.
    _chain.add_handler(handlers.JavaMidletHandler(generic_normalizers))

    # Smart TVs.
    _chain.add_handler(handlers.SmartTVHandler(generic_normalizers))

    # Mobile devices.
    kindle_normalizer = generic_normalizers.add_normalizer(specific.Kindle())
    _chain.add_handler(handlers.KindleHandler(kindle_normalizer))
    lguplus_normalizer = generic_normalizers.add_normalizer(specific.LGUPLUS())
    _chain.add_handler(handlers.LGUPLUSHandler(lguplus_normalizer))

    # Mobile platforms.
    android_normalizer = generic_normalizers.add_normalizer(specific.Android())
    _chain.add_handler(handlers.AndroidHandler(android_normalizer))

    _chain.add_handler(handlers.AppleHandler(generic_normalizers))
    _chain.add_handler(handlers.WindowsPhoneDesktopHandler(generic_normalizers))
    _chain.add_handler(handlers.WindowsPhoneHandler(generic_normalizers))
    _chain.add_handler(handlers.NokiaOviBrowserHandler(generic_normalizers))

    # High workload mobile matchers.
    _chain.add_handler(handlers.NokiaHandler(generic_normalizers))
    _chain.add_handler(handlers.SamsungHandler(generic_normalizers))
    _chain.add_handler(handlers.BlackBerryHandler(generic_normalizers))
    _chain.add_handler(handlers.SonyEricssonHandler(generic_normalizers))
    _chain.add_handler(handlers.MotorolaHandler(generic_normalizers))

    # Other mobile matchers.
    _chain.add_handler(handlers.AlcatelHandler(generic_normalizers))
    _chain.add_handler(handlers.BenQHandler(generic_normalizers))
    _chain.add_handler(handlers.DoCoMoHandler(generic_normalizers))
    _chain.add_handler(handlers.GrundigHandler(generic_normalizers))

    htc_mac_normalizer = generic_normalizers.add_normalizer(specific.HTCMac())
    _chain.add_handler(handlers.HTCMacHandler(htc_mac_normalizer))

    _chain.add_handler(handlers.HTCHandler(generic_normalizers))
    _chain.add_handler(handlers.KDDIHandler(generic_normalizers))
    _chain.add_handler(handlers.KyoceraHandler(generic_normalizers))

    lg_normalizer = generic_normalizers.add_normalizer(specific.LG())
    _chain.add_handler(handlers.LGHandler(lg_normalizer))

    _chain.add_handler(handlers.MitsubishiHandler(generic_normalizers))
    _chain.add_handler(handlers.NecHandler(generic_normalizers))
    _chain.add_handler(handlers.NintendoHandler(generic_normalizers))
    _chain.add_handler(handlers.PanasonicHandler(generic_normalizers))
    _chain.add_handler(handlers.PantechHandler(generic_normalizers))
    _chain.add_handler(handlers.PhilipsHandler(generic_normalizers))
    _chain.add_handler(handlers.PortalmmmHandler(generic_normalizers))
    _chain.add_handler(handlers.QtekHandler(generic_normalizers))
    _chain.add_handler(handlers.ReksioHandler(generic_normalizers))
    _chain.add_handler(handlers.SagemHandler(generic_normalizers))
    _chain.add_handler(handlers.SanyoHandler(generic_normalizers))
    _chain.add_handler(handlers.SharpHandler(generic_normalizers))
    _chain.add_handler(handlers.SiemensHandler(generic_normalizers))
    _chain.add_handler(handlers.SPVHandler(generic_normalizers))
    _chain.add_handler(handlers.ToshibaHandler(generic_normalizers))
    _chain.add_handler(handlers.VodafoneHandler(generic_normalizers))

    webos_normalizer = generic_normalizers.add_normalizer(specific.WebOS())
    _chain.add_handler(handlers.WebOSHandler(webos_normalizer))

    _chain.add_handler(handlers.OperaMiniHandler(generic_normalizers))

    # Robots / Crawlers.
    _chain.add_handler(handlers.BotCrawlerTranscoderHandler(generic_normalizers))

    # Desktop Browsers.
    chrome_normalizer = generic_normalizers.add_normalizer(specific.Chrome())
    _chain.add_handler(handlers.ChromeHandler(chrome_normalizer))

    firefox_normalizer = generic_normalizers.add_normalizer(specific.Firefox())
    _chain.add_handler(handlers.FirefoxHandler(firefox_normalizer))

    msie_normalizer = generic_normalizers.add_normalizer(specific.MSIE())
    _chain.add_handler(handlers.MSIEHandler(msie_normalizer))

    opera_normalizer = generic_normalizers.add_normalizer(specific.Opera())
    _chain.add_handler(handlers.OperaHandler(opera_normalizer))

    safari_normalizer = generic_normalizers.add_normalizer(specific.Safari())
    _chain.add_handler(handlers.SafariHandler(safari_normalizer))

    konqueror_normalizer = generic_normalizers.add_normalizer(specific.Konqueror())
    _chain.add_handler(handlers.KonquerorHandler(konqueror_normalizer))

    # All other requests.
    _chain.add_handler(handlers.CatchAllHandler(generic_normalizers))


def _create_generic_normalizers():
    '''
    @see WURFL PHP 'WURFL_UserAgentHandlerChainFactory'.
    '''
    return normalizers.UserAgentNormalizer([
        generic.UPLink(),
        generic.BlackBerry(),
        generic.YesWAP(),
        generic.BabelFish(),
        generic.SerialNumbers(),
        generic.NovarraGoogleTranslator(),
        generic.LocaleRemover(),
        generic.UCWEB(),
    ])


_init()
