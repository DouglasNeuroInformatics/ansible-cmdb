<%
import json

class CustEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            # Sort, so 'groups' does not come out in a different order on
            # every run.
            return sorted(obj)
        return json.JSONEncoder.default(self, obj)

print(json.dumps(hosts, indent=2, cls=CustEncoder))
%>
