# Generated by Django 5.1 on 2024-08-29 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrainerSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jumlah_sesi', models.IntegerField()),
                ('status', models.CharField(choices=[('Proses', 'Proses'), ('Selesai', 'Selesai')], default='Proses', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=100)),
                ('mulai', models.DateTimeField()),
                ('selesai', models.DateTimeField()),
                ('deskripsi', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
