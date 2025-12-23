from django.db import migrations

#roles are seller, buyer, admin, superadmin

def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    seller_group, _ = Group.objects.get_or_create(name="seller")
    buyer_group, _ = Group.objects.get_or_create(name="buyer")
    admin_group, _ = Group.objects.get_or_create(name="admin")
    #superadmin has access to everything, no need to create a group


    seller_perms = Permission.objects.filter(
        codename__in = [
            #auth
            "user_account_detail",
            "user_account_update",
            "user_role_update",
            "user_activate_account",
            "user_decativate_account",
            "user_change_password",
            #products
            "create_product",
            "list_approved_products",
            "list_unapproved_products"
            "view_product_details",
            "update_product_details",
            "view_reviews",
            #order
            "confirm_payment",
            "view_delivery_details",
            "deliver_order",
            #dispute
            "view_disputes",
            "acknowledge_dispute",
            "respond_to_dispute",
        ]
    )

    buyer_perms = Permission.objects.filter(
        codename__in = [
            #auth
            "user_account_detail",
            "user_account_update",
            "user_role_update",
            "user_activate_account",
            "user_decativate_account",
            "user_change_password",
            #products
            "list_approved_products",
            "view_product_details",
            "review_product",
            "delete_review",
            "edit review",
            "view_reviews",
            #cart
            "add_item_to_cart",
            "remove_item_from_cart",
            "clear_cart",
            #order
            "create_order",
            "view_order",
            "view_order_item",
            "edit_order",
            "cancel_order",
            "save_order",
            "pay_order",
            "generate_reciept",
            "view_delivery_details",
            "recieve_order_delivery",
            #dispute
            "create_dispute",
            "view_self_disputes",
            "cancel_dispute",
            "escalate_dispute",
            "satisfy_dispute",
        ]
    )

    admin_perms = Permission.objects.filter(
        codename__in = [
            #auth
            "user_list_accounts",
            "user_account_detail",
            "user_approve_role",
            "user_account_update",
            "user_change_password",
            "user_ban_account",
            "user_unban_account",
            #product
            "list_products",
            "approve_product",
            "disprove_product",
            "view_product_details",
            "view_reviews",
            "delete_any_review",
            #order
            "view_all_orders",
            "view_delivery_details",
            #dispute
            "view_disputes",
            "cancel_dispute",
            "resolve_dispute",
            "view_escalated_disputes",
            "resolve_escalated_disputes",
        ]
    )

    seller_group.permissions.set(seller_perms)
    buyer_group.permissions.set(buyer_perms)
    admin_group.permissions.set(admin_perms)

class Migration(migrations.Migration):

    dependencies = [
        ('katakara_auth', '0001_initial'),
        ('katakara_auth', '0002_katakarauser_bio_alter_katakarauser_is_active'),
        ('katakara_auth', '0003_alter_katakarauser_options'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions)
    ]