"""DER: Animal guarda data_nascimento (a idade passa a ser calculada)."""
import datetime

from django.db import migrations, models


def idade_para_data_nascimento(apps, schema_editor):
    """Converte a idade (anos) em data aproximada: mesmo dia e mês de hoje."""
    Animal = apps.get_model('agendamentos', 'Animal')
    hoje = datetime.date.today()
    for animal in Animal.objects.exclude(idade__isnull=True):
        ano = hoje.year - animal.idade
        try:
            animal.data_nascimento = hoje.replace(year=ano)
        except ValueError:  # 29/02 em ano não bissexto
            animal.data_nascimento = hoje.replace(year=ano, day=28)
        animal.save(update_fields=['data_nascimento'])


def data_nascimento_para_idade(apps, schema_editor):
    Animal = apps.get_model('agendamentos', 'Animal')
    hoje = datetime.date.today()
    for animal in Animal.objects.exclude(data_nascimento__isnull=True):
        nasc = animal.data_nascimento
        animal.idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        animal.save(update_fields=['idade'])


class Migration(migrations.Migration):
    dependencies = [('agendamentos', '0002_consulta_disponibilidade')]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='data_nascimento',
            field=models.DateField(
                blank=True, null=True, verbose_name='Data de nascimento',
                help_text='Se não souber a data exata, informe uma aproximada.'),
        ),
        migrations.RunPython(idade_para_data_nascimento, data_nascimento_para_idade),
        migrations.RemoveField(model_name='animal', name='idade'),
    ]
