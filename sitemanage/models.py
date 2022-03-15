from django.db import models
from django.contrib.sites.models import Site

class SiteConfig(models.Model):
    site = models.OneToOneField(Site, verbose_name='Site', on_delete=models.PROTECT)
    meta_title = models.CharField('meta_title', max_length=100)
    meta_description = models.CharField('meta_description', max_length=300)
    meta_keywords = models.CharField('SEO_keywords', max_length=300)
    administrator = models.CharField('administrator', max_length=30)
    top_title = models.CharField('top_title', max_length=100)
    top_sub_title = models.CharField('top_sub_title', max_length=200)
    

    def __str__(self):
        return self.meta_title