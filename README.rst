**WURFL Python** allows matching user agent strings with devices in the `WURFL database <http://wurfl.sourceforge.net>`_ (Wireless Universal Resource File) using Python. Matching strategies have been directly ported from `WURFL PHP <http://wurfl.sourceforge.net/php_index.php>`_ library (v1.4.1 at the moment). However, unlike WURFL PHP, WURFL Python focus **only** on matching user agents with devices in the WURFL database. Specifically,

- No caching infrastructure is provided, but you can implement it trivialy in your application. You know better than me what's the best caching strategy in your scenario.

- Only 'accuracy' matching mode is provided. You don't need 'performance' mode. No, you don't. What you need is a reasonable caching layer.

- Facilities for editing or making creative queries on the WURFL database are not provided. Use something else for that. That's out of the scope of this project.

In order to make life easier when syncing with future changes in WURFL PHP, WURFL Python intentionally mimics the implementation of the core matching features in WURFL PHP. If you notice any different behavior between WURFL PHP and WURFL Python, please, `post an issue <https://github.com/carlosabalde/wurfl-python/issues>`_ providing some user agent example.

Current reference PHP implementation (1.4.1) is available in `extras/wurfl-php <https://github.com/carlosabalde/wurfl-python/tree/master/extras/wurfl-php>`_.

QuickStart
==========

1. Install WURFL Python::

    ~$ pip install wurfl-python

2. Download latest version of the `WURFL database <http://wurfl.sourceforge.net/wurfl_download.php>`_.

3. Convert XML database in a convenient Python module. If you're not interested in all capabilities in the database, you can reduce size of the output Python module selecting only those capability groups you are interested in::

    ~$ wurfl-python-processor /path/to/wurfl.xml --output=wurfl.py --group product_info --group display

4. Copy the generated module into your project and start matching user agents::

    >>> import wurfl

    >>> device = wurfl.match(u'Mozilla/5.0 (iPad; CPU OS 6_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B141 [FBAN/FBIOS;FBAV/6.0.1;FBBV/180945;FBDV/iPad3,4;FBMD/iPad;FBSN/iPhone OS;FBSV/6.1;FBSS/2; FBCR/;FBID/tablet;FBLC/zh_TW;FBOP/1]')

    >>> print device.id
    apple_ipad_ver1_sub6

    >>> print device.brand_name
    Apple

    >>> print device.model_name
    iPad

    >>> device = wurfl.find(u'samsung_gt_i7500_ver1')

    >>> print device.model_name
    GT i7500

Alternatives
============

Closest Python alternative project is `pywurfl <https://pypi.python.org/pypi/pywurfl/>`_. Unfortunattly, pywurfl has been unmaintained for some years.
