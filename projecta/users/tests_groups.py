import pytest
from django.contrib.auth.models import Group

pytestmark = pytest.mark.django_db


class TestDefaultGroups:
    def test_groups_are_created_by_migration(self):
        names = set(Group.objects.values_list("name", flat=True))
        assert {"Customer", "Manager", "Staff"}.issubset(names)

    def test_customer_can_view_books_but_not_add(self):
        group = Group.objects.get(name="Customer")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert "view_book" in codenames
        assert "add_book" not in codenames

    def test_manager_can_manage_catalog(self):
        group = Group.objects.get(name="Manager")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert {"add_book", "change_book", "view_book"} <= codenames
        # Manager cannot delete books — only Staff can
        assert "delete_book" not in codenames

    def test_staff_has_delete_permissions(self):
        group = Group.objects.get(name="Staff")
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert {"delete_book", "delete_order", "view_user"} <= codenames
