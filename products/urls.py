from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # hinzufuegen einer View mit dem Namen product_list
    path('', views.show_webpage, name='show_webpage'),
    path('add_product/', views.add_prod, name='add_prod'),
    path('delete_product/', views.delete_prod, name='delete_prod'),
    path('product_list/', views.product_list, name='product_list'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

