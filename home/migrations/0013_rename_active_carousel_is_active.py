# Generated by Django 3.2 on 2021-05-02 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_carousel_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carousel',
            old_name='active',
            new_name='is_active',
        ),
    ]
