import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_books_featured_image_books_harga_potongan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='featured_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=app.models.rename_featured_image),
        ),
        migrations.AlterField(
            model_name='mediabooks',
            name='media',
            field=models.ImageField(max_length=255, upload_to=app.models.rename_media_books),
        ),
    ]
