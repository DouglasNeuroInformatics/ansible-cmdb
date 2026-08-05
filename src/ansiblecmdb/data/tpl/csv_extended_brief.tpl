<%

import sys
import csv
import logging

log = logging.getLogger(__name__)

cols = [
  {"title": "Name",       "id": "name",       "visible": True, "field": lambda h: h.get('name', '')},
  {"title": "IP",         "id": "ip",         "visible": True, "field": lambda h: host['ansible_facts'].get('ansible_default_ipv4', {}).get('address', '')},
  {"title": "OS",         "id": "os",         "visible": True, "field": lambda h: h['ansible_facts'].get('ansible_distribution', '') + ' ' + h['ansible_facts'].get('ansible_distribution_version', '')},
  {"title": "Virt",       "id": "virt",       "visible": True, "field": lambda h: host['ansible_facts'].get('ansible_virtualization_type', 'Unk') + '/' + host['ansible_facts'].get('ansible_virtualization_role', 'Unk')},
  {"title": "vCPUs",       "id": "vcpus",       "visible": True, "field": lambda h: str(host['ansible_facts'].get('ansible_processor_vcpus', 0))},
  {"title": "CPU Type",       "id": "cpus",       "visible": True, "field": lambda h: list(host['ansible_facts'].get('ansible_processor',[]))[-1] if isinstance(host['ansible_facts'].get('ansible_processor',0),list) else "unknown"},
  {"title": "Mem",        "id": "mem",        "visible": True, "field": lambda h: '%0.0fg' % (int(host['ansible_facts'].get('ansible_memtotal_mb', 0)) / 1000.0)},
  {"title": "Product Name", "id": "product_name", "visible": True, "field": lambda h: host['ansible_facts'].get('ansible_product_name', '')},
]

# Enable columns specified with '--columns'
if columns is not None:
  for col in cols:
    if col["id"] in columns:
      col["visible"] = True
    else:
      col["visible"] = False

def get_cols():
  return [col for col in cols if col['visible'] is True]

fieldnames = []
for col in get_cols():
  fieldnames.append(col['title'])

writer = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(fieldnames)
for hostname, host in sorted(hosts.items()):
  if 'ansible_facts' not in host:
    log.warning(u'{0}: No info collected.'.format(hostname))
  else:
    out_cols = []
    for col in get_cols():
      out_cols.append(col['field'](host))
    writer.writerow(out_cols)
%>
