# Generated by Django 3.2 on 2023-07-07 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20201025_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='picture',
            field=models.ImageField(default='default.png', upload_to='media'),
        ),
    ]
