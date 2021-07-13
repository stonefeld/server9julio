# Generated by Django 3.1.4 on 2020-12-09 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='deuda',
            field=models.FloatField(null=True, verbose_name='Deuda'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='general',
            field=models.BooleanField(default=False, verbose_name='General'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='pileta',
            field=models.BooleanField(default=False, verbose_name='Pileta'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='tenis',
            field=models.BooleanField(default=False, verbose_name='Tenis'),
        ),
    ]