# Generated by Django 4.0.5 on 2022-06-03 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='layer',
        ),
        migrations.AddField(
            model_name='layer',
            name='attributes',
            field=models.ManyToManyField(to='generator.attribute'),
        ),
    ]
