from .models import Panier, ProduitPanier

def panier_context(request):
    panier_id = request.session.get('panier_id')
    produits = []
    total_produits = 0

    if panier_id:
        try:
            panier = Panier.objects.get(id=panier_id)
            produits = ProduitPanier.objects.filter(panier=panier)
            total_produits = sum(item.produit.prix * item.quantite for item in produits)
        except Panier.DoesNotExist:
            pass

    return {
        'mini_panier_produits': produits,
        'total_produits': total_produits,
    }


