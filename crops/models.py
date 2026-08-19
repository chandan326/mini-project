from django.db import models
from django.utils.text import slugify

class Crop(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="English crop name e.g. Tomato")
    name_hi = models.CharField(max_length=100, blank=True, null=True, help_text="Hindi crop name e.g. टमाटर")
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, default='fa-seedling', help_text="FontAwesome icon class e.g. fa-pepper-hot")
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Crop'
        verbose_name_plural = 'Crops'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        from django.utils.translation import get_language
        lang = get_language()
        if lang and lang.startswith('hi') and self.name_hi:
            return self.name_hi
        return self.name

    def __str__(self):
        if self.name_hi:
            return f"{self.name} ({self.name_hi})"
        return self.name
