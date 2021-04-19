# Generated by Django 3.1.6 on 2021-04-13 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estacionamiento', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cicloanual',
            options={'verbose_name': 'Ciclo Anual', 'verbose_name_plural': 'Ciclos Anuales'},
        ),
        migrations.AlterModelOptions(
            name='ciclocaja',
            options={'verbose_name': 'Ciclo Caja', 'verbose_name_plural': 'Ciclos Caja'},
        ),
        migrations.AlterModelOptions(
            name='ciclomensual',
            options={'verbose_name': 'Ciclo Mensual', 'verbose_name_plural': 'Ciclos Mensuales'},
        ),
        migrations.AlterModelOptions(
            name='proveedor',
            options={'verbose_name': 'Proveedor', 'verbose_name_plural': 'Proveedores'},
        ),
        migrations.AlterModelOptions(
            name='registroestacionamiento',
            options={'verbose_name': 'Registro Estacionamiento', 'verbose_name_plural': 'Registros Estacionamiento'},
        ),
        migrations.AlterField(
            model_name='registroestacionamiento',
            name='direccion',
            field=models.CharField(choices=[('ENTRADA', 'ENTRADA'), ('SALIDA', 'SALIDA')], default='ENTRADA', max_length=30, verbose_name='Dirección'),
        ),
        migrations.AlterField(
            model_name='registroestacionamiento',
            name='tipo',
            field=models.CharField(choices=[('SOCIO', 'SOCIO'), ('SOCIO-MOROSO', 'SOCIO-MOROSO'), ('NOSOCIO', 'NOSOCIO'), ('PROVEEDOR', 'PROVEEDOR')], default='SOCIO', max_length=30, verbose_name='Tipo'),
        ),
    ]