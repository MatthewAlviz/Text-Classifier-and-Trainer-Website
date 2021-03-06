# Generated by Django 2.1.4 on 2018-12-26 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrainedModels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filePath', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('dateCreated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('email', models.EmailField(max_length=250, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='trainedmodels',
            name='email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Webapp.UserInfo'),
        ),
    ]
