# Generated by Django 4.0.3 on 2022-03-05 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="task",
            old_name="time_to_process",
            new_name="processing_time",
        ),
    ]
