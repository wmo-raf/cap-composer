from django.utils.translation import gettext_lazy
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.api.v2.utils import get_full_url
from wagtailcache.cache import WagtailCacheMixin
from wagtailmetadata.models import MetadataPageMixin as BaseMetadataPageMixin


class MetadataPageMixin(BaseMetadataPageMixin, WagtailCacheMixin):
    class Meta:
        abstract = True
    
    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("slug", widget=SlugInput),
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel('search_image'),
            ],
            gettext_lazy("For search engines"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_in_menus"),
            ],
            gettext_lazy("For site menus"),
        ),
    ]
    
    def get_meta_image_url(self, request):
        meta_image = self.get_meta_image_rendition()
        if meta_image:
            return get_full_url(request, meta_image.url)
        return None
