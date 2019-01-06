# Generated by Django 2.1.4 on 2019-01-03 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Webapp', '0002_registrationqueue'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangePassQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticketNo', models.CharField(max_length=20, unique=True)),
                ('dateCreated', models.DateTimeField(auto_now=True)),
                ('reqCount', models.IntegerField()),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Webapp.UserInfo')),
            ],
        ),
    ]