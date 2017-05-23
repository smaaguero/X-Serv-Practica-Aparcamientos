# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('idNumber', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('url', models.TextField()),
                ('phoneNumber', models.TextField()),
                ('mail', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=17, max_digits=20)),
                ('longitude', models.DecimalField(decimal_places=17, max_digits=20)),
                ('neighborhood', models.CharField(max_length=64)),
                ('district', models.CharField(max_length=64)),
                ('accessibility', models.BooleanField()),
                ('numberOfComments', models.IntegerField()),
                ('punctuation', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Selected',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('userName', models.CharField(max_length=64)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('parking', models.ForeignKey(to='parking.Parking')),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('background', models.TextField()),
                ('size', models.IntegerField()),
                ('title', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='parking',
            field=models.ForeignKey(to='parking.Parking'),
        ),
    ]
