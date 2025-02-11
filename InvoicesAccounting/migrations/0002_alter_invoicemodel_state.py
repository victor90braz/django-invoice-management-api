# Generated by Django 5.1.6 on 2025-02-11 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('InvoicesAccounting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicemodel',
            name='state',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('ACCOUNTED', 'Accounted'), ('PAID', 'Paid'), ('CANCELED', 'Canceled'), ('PENDING', 'Pending')], default='DRAFT', max_length=20),
        ),
    ]
