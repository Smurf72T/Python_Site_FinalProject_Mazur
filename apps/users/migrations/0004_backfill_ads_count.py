from django.db import migrations


def backfill_ads_count(apps, schema_editor):
    """Пересчитать счётчик объявлений у существующих профилей."""
    Profile = apps.get_model("users", "Profile")
    Ad = apps.get_model("ads", "Ad")

    for profile in Profile.objects.all().iterator():
        count = Ad.objects.filter(owner_id=profile.user_id).count()
        if profile.ads_count != count:
            Profile.objects.filter(pk=profile.pk).update(ads_count=count)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_profile_options_alter_profile_is_moderator_and_more"),
        ("ads", "0005_alter_ad_deposit_amount_alter_ad_min_rental_days"),
    ]

    operations = [
        migrations.RunPython(backfill_ads_count, migrations.RunPython.noop),
    ]