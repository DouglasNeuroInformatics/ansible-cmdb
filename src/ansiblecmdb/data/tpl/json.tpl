<%
import json

class CustEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            # Sort, so 'groups' does not come out in a different order on
            # every run.
            try:
                return sorted(obj)
            except TypeError:
                # Mixed, non-orderable contents -- a host var loaded from a
                # YAML '!!set' can hold e.g. {1, "1"}. Sort on a key that is
                # always comparable so the output stays deterministic rather
                # than falling back to arbitrary set order.
                return sorted(obj, key=lambda v: (type(v).__name__, str(v)))
        return json.JSONEncoder.default(self, obj)

print(json.dumps(hosts, indent=2, cls=CustEncoder))
%>
