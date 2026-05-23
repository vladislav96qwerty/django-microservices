"""Data migration: create default Customer / Manager / Staff groups."""
from django.db import migrations


GROUPS = {
    "Customer": [
        # Catalog — read-only
        ("books", "view_book"),
        ("books", "view_author"),
        ("books", "view_category"),
        # Reviews — manage own
        ("books", "add_review"),
        ("books", "change_review"),
        ("books", "delete_review"),
        ("books", "view_review"),
        # Orders — create / view own
        ("orders", "add_order"),
        ("orders", "view_order"),
        ("orders", "add_orderitem"),
        ("orders", "view_orderitem"),
    ],
    "Manager": [
        # Catalog — full CRUD except delete
        ("books", "add_book"),
        ("books", "change_book"),
        ("books", "view_book"),
        ("books", "add_author"),
        ("books", "change_author"),
        ("books", "view_author"),
        ("books", "add_category"),
        ("books", "change_category"),
        ("books", "view_category"),
        ("books", "view_review"),
        ("books", "delete_review"),
        # Orders — read + status update
        ("orders", "view_order"),
        ("orders", "change_order"),
        ("orders", "view_orderitem"),
    ],
    "Staff": [
        # Everything Manager has + delete + user mgmt
        ("books", "add_book"),
        ("books", "change_book"),
        ("books", "delete_book"),
        ("books", "view_book"),
        ("books", "add_author"),
        ("books", "change_author"),
        ("books", "delete_author"),
        ("books", "view_author"),
        ("books", "add_category"),
        ("books", "change_category"),
        ("books", "delete_category"),
        ("books", "view_category"),
        ("books", "delete_review"),
        ("books", "view_review"),
        ("orders", "add_order"),
        ("orders", "change_order"),
        ("orders", "delete_order"),
        ("orders", "view_order"),
        ("orders", "view_orderitem"),
        ("orders", "change_orderitem"),
        ("orders", "delete_orderitem"),
        ("users", "view_user"),
        ("users", "change_user"),
    ],
}


def create_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    for group_name, perms in GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for app_label, codename in perms:
            try:
                ct = ContentType.objects.get(
                    app_label=app_label, model=codename.split("_", 1)[1]
                )
                permission = Permission.objects.get(
                    content_type=ct, codename=codename
                )
                group.permissions.add(permission)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                # Skip if model / permission isn't registered yet — keeps
                # the migration idempotent across partial app installs.
                continue


def remove_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=list(GROUPS.keys())).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("books", "0001_initial"),
        ("orders", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
