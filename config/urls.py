from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^email_confirmed/', TemplateView.as_view(template_name='emails/email_confirmed.html')),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

    url(r'^$', TemplateView.as_view(template_name='base.html'), name='home'),
    url(settings.ADMIN_URL, include(admin.site.urls)),
    url('^api/', include('config.api_urls', namespace='api')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^events/', include('good_spot.events.urls')),

]

if settings.USE_SILK:
    urlpatterns += [
        url(r'^silk/', include('silk.urls', namespace='silk'))
    ]

if settings.USE_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
