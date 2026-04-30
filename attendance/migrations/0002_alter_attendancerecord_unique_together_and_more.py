

import django.db.models.deletion

from django.conf import settings

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [

('attendance', '0001_initial'),

]

operations = [

migrations.AlterUniqueTogether(

name='attendancerecord',

unique_together=set(),

),

migrations.AlterUniqueTogether(

name='attendancesession',

unique_together=set(),

),

migrations.RemoveField(

model_name='student',

name='parent_user',

),

migrations.AddField(

model_name='student',

name='parent',

field=models.ForeignKey(blank=True, limit_choices_to={'role': 'parent'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to=settings.AUTH_USER_MODEL),

),

migrations.AlterField(

model_name='attendancerecord',

name='student',

field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.student'),

),

migrations.AlterField(

model_name='attendancesession',

name='trainer',

field=models.ForeignKey(limit_choices_to={'role': 'trainer'}, on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL),

),

migrations.AddConstraint(

model_name='attendancerecord',

constraint=models.UniqueConstraint(fields=('session', 'student'), name='unique_session_student_record'),

),

migrations.AddConstraint(

model_name='attendancesession',

constraint=models.UniqueConstraint(fields=('student_class', 'date'), name='unique_class_date_session'),

),

]

