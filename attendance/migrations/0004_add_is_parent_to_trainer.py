
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_alter_trainer_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainer',
            name='is_parent',
            field=models.BooleanField(default=False),
        ),
    ]
