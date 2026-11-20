from types import SimpleNamespace
from unittest.mock import Mock, patch

from frappe.desk import search
from frappe.tests import UnitTestCase


class TestLinkSearchImages(UnitTestCase):
	def setUp(self):
		super().setUp()
		self.backend = Mock()
		meta = self.backend.get_meta.return_value
		meta.image_field = "image"
		meta.get_field.return_value = SimpleNamespace(permlevel=0, is_virtual=False)
		self.fields = Mock(return_value=["name", "image"])
		for target, value in (("frappe", self.backend), ("get_permitted_fields", self.fields)):
			p = patch.object(search, target, value)
			p.start()
			self.addCleanup(p.stop)

	def test_select_only_image_is_not_queried(self):
		self.fields.return_value = ["name"]
		rows = [{"value": "_Test Record"}]
		search.add_images(rows, "_Test DocType")
		self.backend.get_list.assert_not_called()
		self.assertNotIn("image", rows[0])

	def test_missing_image_column_is_safe(self):
		self.backend.get_list.return_value = [{"name": "_Test Record"}]
		rows = [{"value": "_Test Record"}]
		search.add_images(rows, "_Test DocType")
		self.assertNotIn("image", rows[0])
		self.assertFalse(self.backend.get_list.call_args.kwargs["as_list"])

	def test_images_follow_record_identity_and_permissions(self):
		self.backend.get_list.return_value = [{"name": "_Test B", "image": "/files/synthetic.png"}]
		rows = [{"value": "_Test A"}, {"value": "_Test B"}]
		search.add_images(rows, "_Test DocType")
		self.assertNotIn("image", rows[0])
		self.assertEqual(rows[1]["image"], "/files/synthetic.png")
		self.assertNotIn("ignore_permissions", self.backend.get_list.call_args.kwargs)

	def test_no_read_permission_hides_images(self):
		self.backend.has_permission.return_value = False
		search.add_images([{"value": "_Test Record"}], "_Test DocType")
		self.backend.get_list.assert_not_called()
