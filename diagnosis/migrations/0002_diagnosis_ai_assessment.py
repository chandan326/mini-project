from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('diagnosis', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='diagnosis', name='ai_assessment',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
