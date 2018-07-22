# --------------------------------------------------------------------
# Copyright 2016, 2018 Cisco Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
# --------------------------------------------------------------------

def walk_fields(self, fields, pfx=""):
    lines = []
    is_keys = False
    if pfx == '/content':
        pfx = ''
        lines.append('')
    elif pfx == '/keys':
        pfx = ''
        is_keys = True
        lines.append('')
    for field in fields:
        if field.fields:
            lines += self.walk_fields(field.fields, pfx + '/' + field.name)
        else:
            value = None
            if field.HasField('bytes_value'):
                value = field.bytes_value
            elif field.HasField('string_value'):
                value = field.string_value
            if field.HasField('bool_value'):
                value = field.bool_value
            elif field.HasField('sint32_value'):
                value = field.sint32_value
            elif field.HasField('sint64_value'):
                value = field.sint64_value
            elif field.HasField('uint32_value'):
                value = field.uint32_value
            elif field.HasField('uint64_value'):
                value = field.uint64_value
            elif field.HasField('double_value'):
                value = field.double_value
            elif field.HasField('float_value'):
                value = field.float_value
            if value is None:
                continue
            if is_keys:
                lines.append("{0:17} : {1:20} : {2}".format(
                    'Key', pfx + '/' + field.name, value))
            else:
                lines.append("{0:80} : {1}".format(
                    pfx + '/' + field.name, value))
    return lines
