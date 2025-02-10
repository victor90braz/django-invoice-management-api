from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=255)),
                ('concept', models.TextField()),
                ('base_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('vat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('state', models.CharField(choices=[('draft', 'Draft'), ('accounted', 'Accounted'), ('paid', 'Paid'), ('canceled', 'Canceled'), ('pending', 'Pending')], default='draft', max_length=20)),
            ],
        ),
    ]
