from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0007_alter_user_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_used_trial',
            field=models.BooleanField(default=False),
        ),
    ] 