import click

from frappe.commands.site import restore
from frappe.tests import UnitTestCase


class TestRestoreAgentCompatibility(UnitTestCase):
	def parse(self, *args):
		with restore.make_context("restore", ["synthetic.sql", *args]) as context:
			return context.params

	def test_existing_arguments_still_parse(self):
		self.assertEqual(self.parse()["sql_file_path"], "synthetic.sql")

	def test_legacy_agent_scope_is_accepted_without_changing_restore_arguments(self):
		self.assertEqual(self.parse("--mariadb-user-host-login-scope", "%"), self.parse())

	def test_other_scopes_are_rejected_before_restore(self):
		with self.assertRaises(click.BadParameter):
			self.parse("--mariadb-user-host-login-scope", "localhost")
