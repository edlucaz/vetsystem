"""Relacionamento "verifica" do DER: FK Consulta → Disponibilidade, preenchida pelo dia da semana."""
import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def vincular_disponibilidade(apps, schema_editor):
    Consulta = apps.get_model('agendamentos', 'Consulta')
    Disponibilidade = apps.get_model('agendamentos', 'Disponibilidade')
    por_dia = {d.dia_da_semana: d for d in Disponibilidade.objects.all()}
    for consulta in Consulta.objects.all():
        consulta.disponibilidade = por_dia.get(timezone.localtime(consulta.data_hora).weekday())
        consulta.save(update_fields=['disponibilidade'])


class Migration(migrations.Migration):
    dependencies = [('agendamentos', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='consulta',
            name='disponibilidade',
            field=models.ForeignKey(
                blank=True, editable=False, null=True,
                on_delete=django.db.models.deletion.SET_NULL, related_name='consultas',
                to='agendamentos.disponibilidade', verbose_name='Disponibilidade verificada'),
        ),
        migrations.RunPython(vincular_disponibilidade, migrations.RunPython.noop),
    ]
