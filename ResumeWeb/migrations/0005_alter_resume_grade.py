# Generated by Django 4.1.7 on 2023-05-03 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ResumeWeb', '0004_alter_resume_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='grade',
            field=models.IntegerField(blank=True, max_length=1, null=True),
        ),
    ]
