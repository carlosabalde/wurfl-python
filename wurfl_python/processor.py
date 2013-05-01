# -*- coding: utf-8 -*-

"""
:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
import sys
import codecs
from time import ctime
from optparse import OptionParser

try:
    from xml.etree.ElementTree import parse
except ImportError:
    try:
        from cElementTree import parse
    except ImportError:
        from elementtree.ElementTree import parse

from wurfl_python.exceptions import DeferredDeviceException


class Device(object):
    def __init__(self, device, groups):
        '''
        @param device: An elementtree.Element instance of a device element in
                       a WURFL XML file.
        @type device: elementtree.Element
        @param groups: None or set of WURFL capability group names.
        @type groups: set
        '''
        self.ua = device.attrib[u'user_agent']
        self.id = device.attrib[u'id']
        self.parent = device.attrib[u'fall_back']
        self.actual_device_root = \
            u'actual_device_root' in device.attrib and \
            device.attrib[u'actual_device_root'].lower() == u'true'
        self.capabilities = {}
        for group in device:
            if groups is None or group.attrib['id'] in groups:
                for capability in group:
                    self.capabilities[capability.attrib['name']] = capability.attrib['value']


class Processor(object):
    def __init__(self, input, groups, output):
        '''
        @param input: WURFL XML file path. It can be a regular, zip, bzip2
                      or gzipped file.
        @type input: string
        @param groups: None or list of WURFL capability group names.
        @type groups: list
        @param output: Python database file path.
        @type output: string
        '''
        # Capability groups.
        self.groups = set(groups) if groups is not None else None

        # XML input.
        if input.endswith('.gz'):
            import gzip
            input = gzip.open(input, 'rb')
        elif input.endswith('.bz2'):
            from bz2 import BZ2File
            input = BZ2File(input)
        elif input.endswith('.zip'):
            from zipfile import ZipFile
            from cStringIO import StringIO
            zfile = ZipFile(input)
            input = StringIO(zfile.read(zfile.namelist()[0]))
        else:
            input = open(input, 'rb')
        self.tree = parse(input)

        # Python output.
        self.output = codecs.open(output, 'wb', 'utf8')

        # Fetch normalized capability types.
        self._load_capability_types()

    def process(self):
        # Initialice.
        self.deferred = {}
        self.done = set()

        # Dump Python header.
        self._dump_header()

        # Process devices.
        for item in self.tree.getroot().find('devices'):
            # Instantiate device.
            device = Device(item, self.groups)

            # Ready to dump?
            if device.parent != 'root' and (device.parent not in self.done):
                if device.parent not in self.deferred:
                    self.deferred[device.parent] = []
                self.deferred[device.parent].append(device)
            else:
                self.done.add(device.id)
                self._dump_device(device)
                self._process_deferred()

        # Process deferred devices.
        while self.deferred:
            deferred_len = len(self.deferred)
            self._process_deferred()
            if deferred_len == len(self.deferred):
                raise DeferredDeviceException('%s devices still deferred: %s' % (deferred_len, self.deferred.keys()))

    def _process_deferred(self):
        '''
        Called to process any deferred devices (devices that have been defined
        in the WURFL before their fall_back has been defined). It is called
        after any device has been handled and also called in a loop
        after all device definitions in the WURFL database have been exhausted.
        '''
        dumped = []
        for parent in self.deferred:
            if parent in self.done:
                for device in self.deferred[parent]:
                    self.done.add(device.id)
                    self._dump_device(device)
                dumped.append(parent)
        for id in dumped:
            del self.deferred[id]

    def _dump_header(self):
        self.output.write(u"# -*- coding: utf-8 -*-\n")
        self.output.write(u"# Generated on: %s.\n" % ctime())
        self.output.write(u"# Version: %s.\n\n" % self.tree.findtext("*/ver").strip())
        self.output.write(u"from __future__ import absolute_import\n")
        self.output.write(u"from wurfl_python import Repository, match, find\n\n")

    def _dump_device(self, device):
        capabilities = []
        for capability in sorted(device.capabilities):
            value = device.capabilities[capability]
            capability_type = self.capability_types.get(capability, None)
            if capability_type == int:
                capabilities.append(u"ur'''%s''':%d" % (capability, int(value.strip())))
            elif capability_type == float:
                capabilities.append(u"ur'''%s''':%f" % (capability, float(value.strip())))
            elif capability_type == bool:
                if value.lower() == u'true':
                    capabilities.append(u"ur'''%s''':True" % capability)
                elif value.lower() == u'false':
                    capabilities.append(u"ur'''%s''':False" % capability)
            else:
                capabilities.append(u"ur'''%s''':ur'''%s'''" % (capability, value))

        self.output.write(u"Repository.register(ur'''%s''', ur'''%s''', %s, {%s}, %s)\n\n" % (
            device.id,
            device.ua if not device.ua.endswith(u'\\') else u'%s\\' % device.ua,
            device.actual_device_root,
            u','.join(capabilities),
            u"ur'''%s'''" % device.parent if device.parent != u'root' else u'None'))

    def _load_capability_types(self):
        self.capability_types = {}
        for capability in self.tree.findall('devices/device/group/capability'):
            name = capability.attrib['name']
            value = capability.attrib['value']
            if name not in self.capability_types:
                try:
                    int(value)
                    self.capability_types[name] = int
                    continue
                except (TypeError, ValueError):
                    pass
                try:
                    float(value)
                    self.capability_types[name] = float
                    continue
                except (TypeError, ValueError):
                    pass

                if value.strip().lower() in ('true', 'false'):
                    self.capability_types[name] = bool
                    continue
                else:
                    self.capability_types[name] = str
            else:
                if self.capability_types[name] == str:
                    continue
                elif self.capability_types[name] == bool:
                    if value.strip().lower() in ('true', 'false'):
                        continue
                    else:
                        self.capability_types[name] = str
                elif self.capability_types[name] == float:
                    try:
                        float(value)
                        continue
                    except (TypeError, ValueError):
                        self.capability_types[name] = str
                elif self.capability_types[name] == int:
                    try:
                        int(value)
                        continue
                    except (TypeError, ValueError):
                        self.capability_types[name] = str


def main():
    option_parser = OptionParser(usage='%prog <WURFL XML file>')
    option_parser.add_option(
        '-o',
        '--output',
        dest='output',
        default='wurfl.py',
        help='Name of the database Python module to produce. Defaults to wurfl.py.')
    option_parser.add_option(
        '-g',
        '--group',
        dest='groups',
        default=None,
        action='append',
        help='Name of a capability group to be included in the output database. If no groups are specified, all input database capabilities groups are included in the output.')

    options, args = option_parser.parse_args()
    if args:
        wurfl = Processor(args[0], options.groups, options.output)
        wurfl.process()
    else:
        sys.stderr.write(option_parser.get_usage())
        sys.exit(1)

if __name__ == '__main__':
    main()
