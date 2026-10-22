"""Histórico de peso do animal (RegistroPeso, Animal 1:N) + carga inicial com o peso atual."""
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def peso_atual_para_historico(apps, schema_editor):
    Animal = apps.get_model('agendamentos', 'Animal')
    RegistroPeso = apps.get_model('agendamentos', 'RegistroPeso')
    hoje = django.utils.timezone.localdate()
    RegistroPeso.objects.bulk_create(
        RegistroPeso(animal_id=animal.pk, peso=animal.peso, data=hoje)
        for animal in Animal.objects.exclude(peso__isnull=True))


class Migration(migrations.Migration):
    dependencies = [('agendamentos', '0003_animal_data_nascimento')]

    operations = [
        migrations.CreateModel(
            name='RegistroPeso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Peso (kg)')),
                ('data', models.DateField(default=django.utils.timezone.localdate, verbose_name='Data da pesagem')),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pesos',
                                             to='agendamentos.animal', verbose_name='Animal')),
            ],
            options={
                'verbose_name': 'Registro de peso',
                'verbose_name_plural': 'Histórico de peso',
                'ordering': ['-data'],
                'constraints': [models.UniqueConstraint(fields=('animal', 'data'), name='peso_unico_por_dia')],
            },
        ),
        migrations.RunPython(peso_atual_para_historico, migrations.RunPython.noop),
    ]
