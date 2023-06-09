# Generated by Django 4.0.3 on 2022-04-16 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(null=True, upload_to='')),
                ('fio', models.CharField(max_length=100)),
                ('birthday', models.DateField(null=True)),
                ('phonenum', models.CharField(max_length=12)),
                ('grade', models.CharField(max_length=10, null=True)),
                ('institution', models.CharField(max_length=100)),
                ('curator', models.CharField(max_length=100)),
                ('spec', models.CharField(max_length=30, null=True)),
                ('skills', models.CharField(max_length=300, null=True)),
                ('projects', models.TextField()),
                ('project_links', models.URLField(max_length=500)),
                ('education', models.CharField(max_length=100, null=True)),
                ('first_lang', models.CharField(max_length=20, null=True)),
                ('other_lang', models.CharField(max_length=300, null=True)),
                ('country', models.CharField(max_length=100, null=True)),
                ('pract_name', models.CharField(max_length=100, null=True)),
                ('pract_period_from', models.DateField(null=True)),
                ('pract_period_to', models.DateField(null=True)),
                ('pract_jobs', models.TextField()),
                ('linkedin', models.URLField(null=True)),
                ('pract_tasks', models.CharField(max_length=100)),
                ('laptop', models.BooleanField()),
            ],
        ),
    ]
