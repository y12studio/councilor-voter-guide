#!/usr/bin/python
# -*- coding: utf-8 -*
import re
import json
import codecs


def write_file(data, file_name):
    file = codecs.open(file_name, 'w', encoding='utf-8')
    file.write(data)
    file.close()

for file_name in ['ilcc/councilors.json', 'ilcc/bills.json', 'ntcc/bills.json', 'ntcc/councilors.json', 'ntcc/councilors_terms.json', 'tccc/bills.json', 'tccc/councilors.json', 'tccc/meeting.json', 'kcc/councilors.json', 'kcc/councilors_terms.json', 'kcc/bills.json', 'tcc/councilors.json', 'tcc/councilors_terms.json', 'tcc/meeting_minutes-2010.json', 'tcc/bills.json', 'tncc/tnccp/tnccp.json']:
    print file_name
    objs = json.load(open(file_name))
    dump_data = json.dumps(objs, sort_keys=True, indent=4, ensure_ascii=False)
    write_file(dump_data, 'pretty_format/%s' % file_name)
