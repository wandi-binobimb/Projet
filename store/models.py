from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import SET_NULL
from django.utils.html import format_html
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from django.apps import apps  # تأكد أن المسار صحيح



# Create your models here.
class SiteStat(models.Model):
    total_visiteurs = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Nombre de visiteurs: {self.total_visiteurs}"

class Categorie(models.Model):
    nom =models.CharField(max_length=100)
    def __str__(self):
        return self.nom

class Produit(models.Model):
    ETIQUETTE_CHOICES = [
        ('NOUVEAU','NOUVEAU'),
        ('PROMO','PROMO'),
        ('PROMO 30%','PROMO 30%'),
        ('SOLDE','SOLDE'),
        ('BIENTÔT ','BIENTÔT '),
        ('','sans'),
    ]
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    nom = models.CharField(max_length=100, verbose_name="nom de l'article")
    description = models.TextField(max_length=100,verbose_name='descrption')
    prix= models.DecimalField(max_digits=10,decimal_places=0)
    etiquette = models.CharField(max_length=20 , choices=ETIQUETTE_CHOICES,blank=True,default='')
    prix_promo = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    vues = models.PositiveIntegerField(default=0)
    stock_restante = models.PositiveIntegerField(default=0, verbose_name="Stock aprés livré")
    prix_achat = models.DecimalField(max_digits=10,decimal_places=0)


    def benefice(self):
        if self.prix and self.prix_achat:
            profit = self.prix - self.prix_achat
            color = "#4CAF50" if profit > 0 else "#F44336"  # أخضر أو أحمر
            return format_html(
                '<span style="color:{};">{} DA</span>',
                color,
                profit
            )
        return "-"

    benefice.short_description = "فائدة المنتج الواحد"

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produit'

class ProduitCouleur(models.Model):
    produit = models.ForeignKey(Produit,on_delete=models.CASCADE,related_name='couleurs')
    couleur = models.CharField(max_length=50 ,blank=True, null=True)  # اسم اللون (ex: Rouge, Bleu)
    code_couleur = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return f"{self.produit.nom}{self.couleur}"



class ProduitImage(models.Model):
    couleur = models.ForeignKey(ProduitCouleur,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='produits/more_images/')

    def __str__(self):
        return f"image de {self.couleur}"

TAILLE_CHOICES = [
    ('36','36'),
    ('37','37'),
    ('38','38'),
    ('39','39'),
    ('40','40'),
    ('41','41'),

    ('XS','XS'),
    ('S','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
]
class ProduitTaille(models.Model):
    # produit = models.ForeignKey(Produit,on_delete=models.CASCADE,related_name='tailles')
    couleur = models.ForeignKey(ProduitCouleur,on_delete=models.CASCADE,related_name='tailles')
    taille = models.CharField(max_length=5,choices=TAILLE_CHOICES)
    stock = models.PositiveIntegerField(default=0)
    stock_vrai = models.PositiveIntegerField(default=0)
    stock_initial = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.couleur}-Taille{self.taille}-stock{self.stock}"






class Wilaya(models.Model):
    nom = models.CharField(max_length=100)
    prix_bureau = models.DecimalField(max_digits=10,decimal_places=0)
    prix_domicile = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.nom

class Commune(models.Model):
    nom = models.CharField(max_length=100)
    wilaya = models.ForeignKey(Wilaya,on_delete=models.CASCADE,related_name='communes')

    def __str__(self):
        return f"{self.nom}({self.wilaya.nom})"


class Client(models.Model):
    nom_complet=models.CharField(max_length=100)
    telephone = models.CharField(max_length=10)
    wilaya = models.ForeignKey(Wilaya,on_delete=models.SET_NULL,null=True)
    commune = models.ForeignKey(Commune,on_delete=SET_NULL,null=True)

    ChOIX_LIVRAISON = [
        ('bureau','توصيل للمكتب'),
        ('a domicile','توصيل للمنزل'),
    ]
    type_livraison = models.CharField(max_length=10,choices=ChOIX_LIVRAISON)


    def __str__(self):
        return self.nom_complet

class Panier(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.client.nom_complet if self.client else 'Anonyme'}"

class ProduitPanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='produits')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    couleur = models.ForeignKey(ProduitCouleur, on_delete=models.CASCADE, blank=True, null=True)
    taille = models.CharField(max_length=5, blank=True, null=True)
    quantite = models.PositiveIntegerField(default=1)
    # stock_vrai_deduit = models.BooleanField(default=False)
    # stock_deduit = models.BooleanField(default=False)
    # stock_restitue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.produit.nom} ({self.couleur.couleur}, {self.taille}) x{self.quantite}"


STATUT_CHOICES = [
        ('en attente', '⏳ En Attente'),
        ('confirmé', '✅ Confirmé'),
        ('en livraison', '🚚 En livraison'),
        ('livré', '📦 Livré'),
        ('retour', '↩️ Retour'),
        ('retournée', '🔄 Retournée'),
    ]

SOURCE_CHOICES = [
    ('site', 'Sponsor_Site'),
    ('messages_site', 'Sponsor_Message'),
    ('facebook', 'Message'),
]

class Commande(models.Model):
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    panier = models.ForeignKey(Panier,on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en attente')
    source = models.CharField(max_length=20,choices=SOURCE_CHOICES,default='site',  # ✅ تلقائيًا من الموقع
verbose_name='مصدر الطلبية'
    )

    total_sans_livraison = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_avec_livraison = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)




    def __str__(self):
        return f"Commande {self.id}-{self.client.nom_complet}"

    def benifice_total(self):
        total = Decimal('0')
        for item in self.panier.produits.all():  # نصل إلى produits من panier
            produit = item.produit
            if produit.prix and produit.prix_achat:
                profit = (Decimal(produit.prix) - Decimal(produit.prix_achat)) * item.quantite
                total += profit

        # نضيف لون جميل للفائدة
        color = "#4CAF50" if total > 0 else "#F44336"
        return format_html('<span style="color:{};">{} DA</span>', color, total)

    benifice_total.short_description = "الفائدة الإجمالية"


    @receiver(post_save, sender='store.Commande')
    def update_benefice_mensuel(sender, instance, **kwargs):
        # نحسب فقط إذا كانت الطلبية تم تسليمها
        if instance.statut != 'livré':
            return  # ⛔ لا نحسب الفائدة إذا لم تكن الطلبية مسلّمة

        mois_actuel = timezone.now().strftime("%B %Y")  # مثال: "October 2025"

        total_benefice_commande = Decimal('0')
        for item in instance.panier.produits.all():
            produit = item.produit
            if produit.prix and produit.prix_achat:
                total_benefice_commande += (Decimal(produit.prix) - Decimal(produit.prix_achat)) * item.quantite

        # تحديث أو إنشاء سجل الشهر الحالي
        benefice_mois, created = BeneficeMensuel.objects.get_or_create(mois=mois_actuel)
        benefice_mois.total_benefice += total_benefice_commande
        benefice_mois.save()


class BeneficeMensuel(models.Model):
    mois = models.CharField(max_length=20, unique=True, verbose_name="الشهر")
    total_benefice = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="مجموع الفائدة")
    date_maj = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    def __str__(self):
        return f"{self.mois} - {self.total_benefice} DA"

    class Meta:
        verbose_name = "الفائدة الشهرية"
        verbose_name_plural = "الفوائد الشهرية"




class RetourMensuel(models.Model):
    mois = models.CharField(max_length=20)
    total_retour = models.PositiveIntegerField(default=0, verbose_name="Commande  en retour")
    total_retournee = models.PositiveIntegerField(default=0, verbose_name="Commande retournée")
    date_maj = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    def __str__(self):
        return f"{self.mois} - Retour: {self.total_retour} / Retournée: {self.total_retournee}"

    class Meta:
        verbose_name = "المرتجعات الشهرية"
        verbose_name_plural = "المرتجعات الشهرية"

class MessageContact(models.Model):
    nom = models.CharField(max_length=100, verbose_name="الاسم")
    telephone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    message = models.TextField(verbose_name="الرسالة")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.telephone})"




from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Commande)
def update_stock_restante(sender, instance, **kwargs):
    """تحديث كمية المنتج المتبقية عند تسليم الطلبية"""
    if instance.statut == 'livré':
        for item in instance.panier.produits.all():
            produit = item.produit
            if produit.stock_restante >= item.quantite:
                produit.stock_restante -= item.quantite
            else:
                produit.stock_restante = 0
            produit.save()


