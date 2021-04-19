# Generated by Django 3.2 on 2021-04-18 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='pics/home.jpg')),
                ('title', models.CharField(max_length=150)),
                ('sub_title', models.CharField(max_length=100)),
            ],
        ),
    ]
