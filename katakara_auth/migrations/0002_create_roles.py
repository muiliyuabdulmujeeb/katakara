from django.db import migrations

#roles are seller, buyer, admin, superadmin

def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    seller_group, _ = Group.objects.get_or_create(name="seller")
    buyer_group, _ = Group.objects.get_or_create(name="buyer")
    admin_group, _ = Group.objects.get_or_create(name="admin")
    superadmin_group, _ = Group.objects.get_or_create(name="superadmin")


    seller_perms = Permission.objects.filter(
        codename__in = []
    )