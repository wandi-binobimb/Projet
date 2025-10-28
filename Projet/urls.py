"""
URL configuration for Projet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shoping_cart/', views.afficher_panier, name='shoping_cart'),
    path("search/", views.search, name="search"),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('index/', views.index, name='index'),
    path('home_02/', views.home_02, name='home_02'),
    path('home_03/', views.home_03, name='home_03'),
    path('product/<int:produit_id>/', views.product_detail, name='product_detail'),
    path('product/', views.liste_produits, name='product'),
    path('panier/', views.panier_view, name='panier'),
    path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/partial/', views.cart_items_partial, name='cart_items_partial'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('confirmer_commande/', views.confirmer_commande, name='confirmer_commande'),
    path('chaussures/promo-solde/', views.chaussures_promo_solde, name='chaussures_promo_solde'),
    path('sacs/promo-solde/', views.sacs_promo_solde, name='sacs_promo_solde'),
    path('get_communes/<int:wilaya_id>/', views.get_communes, name='get_communes'),
    path('get_shipping_options/<int:wilaya_id>/', views.get_shipping_options, name='get_shipping_options'),
    path('admin/get_categorie_nom/', views.get_categorie_nom, name='get_categorie_nom'),
    path('get_tailles/<int:couleur_id>/', views.get_tailles, name='get_tailles'),
    path("quick-view/<int:produit_id>/", views.product_quick_view, name="product_quick_view"),
    path('cart_items_partial/', views.cart_items_partial, name='cart_items_partial'),
    path('mini_panier/', views.mini_panier, name='mini_panier'),

    path('produits/etiquette/<str:etiquette>/', views.produits_par_etiquette, name="produits_par_etiquette"),
]

# === إعداد الميديا في وضع التطوير ===
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
