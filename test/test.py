import sys
import unittest
import importlib.util
import sys
import os

sys.path.insert(0, os.path.realpath("../lib"))
sys.path.insert(0, os.path.realpath("../src"))
import ansiblecmdb


class ExtendTestCase(unittest.TestCase):
    """
    Test the extending of facts.
    """

    def testExtendOverrideParams(self):
        """
        Test that we can override a native fact
        """
        fact_dirs = ["f_extend/out_setup", "f_extend/extend"]
        ansible = ansiblecmdb.Ansible(fact_dirs)
        env_editor = ansible.hosts["debian.dev.local"]["ansible_facts"]["ansible_env"][
            "EDITOR"
        ]
        self.assertEqual(env_editor, "nano")

    def testExtendAddParams(self):
        """
        Test that we can add new facts
        """
        fact_dirs = ["f_extend/out_setup", "f_extend/extend"]
        ansible = ansiblecmdb.Ansible(fact_dirs)
        software = ansible.hosts["debian.dev.local"]["software"]
        self.assertIn("Apache2", software)


class HostParseTestCase(unittest.TestCase):
    """
    Test specifics of the hosts inventory parser
    """

    def testChildGroupHosts(self):
        """
        Test that children groups contain all hosts they should.
        """
        fact_dirs = ["f_hostparse/out"]
        inventories = ["f_hostparse/hosts"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        groups = ansible.hosts["db.dev.local"]["groups"]
        self.assertIn("db", groups)
        self.assertIn("dev", groups)
        self.assertIn("dev_local", groups)

    def testChildGroupVars(self):
        """
        Test that all vars applied against a child group are set on the hosts.
        """
        fact_dirs = ["f_hostparse/out"]
        inventories = ["f_hostparse/hosts"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        host_vars = ansible.hosts["db.dev.local"]["hostvars"]
        self.assertEqual(host_vars["function"], "db")
        self.assertEqual(host_vars["dtap"], "dev")

    def testExpandHostDef(self):
        """
        Verify that host ranges are properly expanded. E.g. db[01-03].local ->
        db01.local, db02.local, db03.local.
        """
        fact_dirs = ["f_hostparse/out"]
        inventories = ["f_hostparse/hosts"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        self.assertIn("web02.dev.local", ansible.hosts)
        self.assertIn("fe03.dev02.local", ansible.hosts)


class LimitTestCase(unittest.TestCase):
    """
    Test the --limit option's pattern parsing.
    """

    def _hosts_for_limit(self, limit):
        fact_dirs = ["f_hostparse/out"]
        inventories = ["f_hostparse/hosts"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories, limit=limit)
        return set(ansible.get_hosts().keys())

    def _parse_limit(self, limit):
        ansible = ansiblecmdb.Ansible.__new__(ansiblecmdb.Ansible)
        return ansible._parse_limit(limit)

    def testLimitColonSeparator(self):
        """
        Verify that ':' separates limit patterns (unchanged behaviour).
        """
        hosts = self._hosts_for_limit("db:web")
        self.assertEqual(hosts, self._hosts_for_limit("db,web"))
        self.assertIn("db.dev.local", hosts)
        self.assertIn("web01.dev.local", hosts)

    def testLimitCommaSeparator(self):
        """
        Verify that ',' also separates limit patterns. Ansible accepts either,
        and prefers the comma for ranges and IPv6 addresses.
        """
        hosts = self._hosts_for_limit("db,web")
        self.assertIn("db.dev.local", hosts)
        self.assertIn("web01.dev.local", hosts)
        self.assertNotIn("fe01.dev01.local", hosts)

    def testLimitCommaExclude(self):
        """
        Verify that '!' exclusion works with the comma separator too.
        """
        hosts = self._hosts_for_limit("db,web,!db")
        self.assertNotIn("db.dev.local", hosts)
        self.assertIn("web01.dev.local", hosts)

    def testLimitEmptyElements(self):
        """
        Verify that doubled and trailing separators are ignored rather than
        producing empty patterns.
        """
        self.assertEqual(
            self._parse_limit("db,,web,"), {"include": ["db", "web"], "exclude": []}
        )
        self.assertEqual(
            self._parse_limit("db::web:"), {"include": ["db", "web"], "exclude": []}
        )

    def testLimitIpv6NotSplit(self):
        """
        Verify that IPv6 literals survive, since they contain ':' themselves.

        Ansible resolves the ambiguity by splitting on ',' when one is present
        and only otherwise falling back to ':', which is why its docs
        recommend the comma for IPv6. A lone IPv6 literal is a single pattern.
        """
        self.assertEqual(
            self._parse_limit("2001:db8::1,web"),
            {"include": ["2001:db8::1", "web"], "exclude": []},
        )
        self.assertEqual(
            self._parse_limit("2001:db8::1"),
            {"include": ["2001:db8::1"], "exclude": []},
        )
        self.assertEqual(
            self._parse_limit("!2001:db8::1"),
            {"include": [], "exclude": ["2001:db8::1"]},
        )

    def testLimitCommaTakesPrecedence(self):
        """
        Verify that a ',' anywhere in the expression makes it a comma list,
        matching ansible.inventory.manager.split_host_pattern -- so 'db:web'
        in 'db:web,frontend' stays one pattern rather than being split.
        """
        self.assertEqual(
            self._parse_limit("db:web,frontend"),
            {"include": ["db:web", "frontend"], "exclude": []},
        )


class InventoryTestCase(unittest.TestCase):
    def testHostsDir(self):
        """
        Verify that we can specify a directory as the hosts inventory file and
        that all files are parsed.
        """
        fact_dirs = ["f_inventory/out"]
        inventories = ["f_inventory/hostsdir"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        host_vars = ansible.hosts["db.dev.local"]["hostvars"]
        groups = ansible.hosts["db.dev.local"]["groups"]
        self.assertEqual(host_vars["function"], "db")
        self.assertIn("db", groups)

    def testDynInv(self):
        """
        Verify that we can specify a path to a dynamic inventory as the
        inventory file, and it will be executed, it's output parsed and added
        as available hosts.
        """
        fact_dirs = ["f_inventory/out"]  # Reuse f_hostparse
        inventories = ["f_inventory/dyninv.py"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        self.assertIn("host5.example.com", ansible.hosts)
        host_vars = ansible.hosts["host5.example.com"]["hostvars"]
        groups = ansible.hosts["host5.example.com"]["groups"]
        self.assertEqual(host_vars["b"], False)
        self.assertIn("atlanta", groups)

    def testMixedDir(self):
        """
        Verify that a mixed dir of hosts files and dynamic inventory scripts is
        parsed correctly.
        """
        fact_dirs = ["f_inventory/out"]
        inventories = ["f_inventory/mixeddir"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories)
        # results from dynamic inventory
        self.assertIn("host4.example.com", ansible.hosts)
        self.assertIn("moocow.example.com", ansible.hosts)
        # results from normal hosts file.
        self.assertIn("web03.dev.local", ansible.hosts)
        # INI file ignored.
        self.assertNotIn("ini_setting", ansible.hosts)


class FactCacheTestCase(unittest.TestCase):
    """
    Test that we properly read fact-cached output dirs.
    """

    def testFactCache(self):
        fact_dirs = ["f_factcache/out"]
        inventories = ["f_factcache/hosts"]
        ansible = ansiblecmdb.Ansible(fact_dirs, inventories, fact_cache=True)
        host_vars = ansible.hosts["debian.dev.local"]["hostvars"]
        groups = ansible.hosts["debian.dev.local"]["groups"]
        ansible_facts = ansible.hosts["debian.dev.local"]["ansible_facts"]
        self.assertIn("dev", groups)
        self.assertEqual(host_vars["dtap"], "dev")
        self.assertIn("ansible_env", ansible_facts)


if __name__ == "__main__":
    unittest.main(exit=True)

    try:
        os.unlink(
            "../src/ansible-cmdbc"
        )  # FIXME: Where is this coming from? Our weird import I assume.
    except Exception:
        pass
