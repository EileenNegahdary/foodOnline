# Generated by Django 5.0.6 on 2024-09-21 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_alter_category_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='food_title',
            field=models.CharField(max_length=50),
        ),
    ]
