



from django.db import migrations, models





class Migration(migrations.Migration):



    dependencies = [

('attendance', '0002_alter_attendancerecord_unique_together_and_more'),

]



operations = [

migrations.AlterField(

model_name='trainer',

name='role',

field=models.CharField(choices=[('trainer', 'Trainer'), ('parent', 'Parent'), ('student', 'Student')], default='student', max_length=20),

),

]

