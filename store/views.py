from gc import get_objects

from django.db.models import Q
from django.template.context_processors import request
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from openpyxl.styles.builtins import total

from django.contrib import messages
from store.models import Produit, ProduitCouleur, ProduitImage, ProduitTaille, Client, Panier, Commande, Wilaya, Commune


from django.db import IntegrityError,transaction
# Create your views here.



def home(request):
    couleurs = ProduitCouleur.objects.select_related('produit').prefetch_related('images')
    return render(request, 'store/index.html', {'couleurs': couleurs})



def about(request):
    return render(request,'store/about.html')



def product(request):
    return render(request,'store/product.html')

def contact(request):
    return render(request,'store/contact.html')

def blog(request):
    return render(request,'store/blog.html')

def index(request):
    return render(request,'store/index.html')

def home_02(request):
    return render(request,'store/home_02.html')

def home_03(request):
    return render(request,'store/home_03.html')






from django.shortcuts import render, get_object_or_404
from store.models import Produit, ProduitCouleur, ProduitImage, ProduitTaille

from .models import Panier, ProduitPanier, Client  # تأكد أنك استوردت هذه النماذج

def product_detail(request, produit_id):

    produit = get_object_or_404(Produit, id=produit_id)

    # زيادة عدد المشاهدات
    produit.vues += 1
    produit.save(update_fields=["vues"])

    # الألوان المتاحة
    couleurs_qs = ProduitCouleur.objects.filter(produit=produit)

    # ✅ نجيب couleur_id من الرابط
    couleur_id_selectionnee = request.GET.get("couleur_id")
    if couleur_id_selectionnee:
        try:
            selected_color_id = int(couleur_id_selectionnee)
        except ValueError:
            selected_color_id = None
    else:
        # إذا ما فيه couleur_id → نأخذ أول لون
        selected_color_id = couleurs_qs.first().id if couleurs_qs.exists() else None

    # نجهّز البيانات
    couleurs_data = []
    for couleur in couleurs_qs:
        images = couleur.images.all()
        tailles = [
            {"taille": t.taille, "stock": t.stock}
            for t in couleur.tailles.all()
        ]
        couleurs_data.append({
            "id": couleur.id,
            "nom": couleur.couleur,
            "code": couleur.code_couleur or "#cccccc",
            "images": [img.image.url for img in images],
            "tailles": tailles,
        })

    panier = get_or_create_panier(request)
    cart_items = ProduitPanier.objects.filter(panier=panier) if panier else []

    # نجيب اللون المختار من قائمة الألوان
    couleur_selectionnee = None
    for c in couleurs_data:
        if c["id"] == selected_color_id:
            couleur_selectionnee = c
            break

    context = {
        "produit": produit,
        "couleurs_data": couleurs_data,

        "cart_items": cart_items,
        "categorie_nom": produit.categorie.nom,
        "selected_color_id": selected_color_id,  # ✅ ضروري
    }

    print("couleur_id_selectionne=",request.GET.get("couleur_id"))
    print("selected_color_id=",selected_color_id)
    return render(request, "store/product_detail.html", context)



def product_quick_view(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    couleurs = produit.couleurs.prefetch_related("images", "tailles")

    # إذا كان الطلب Ajax نرجع partial فقط
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render(request, "store/partials/quick_view_modal.html", {
            "produit": produit,
            "couleurs": couleurs
        }).content.decode("utf-8")
        return JsonResponse({"html": html})

    # fallback: فتح صفحة كاملة
    return render(request, "store/product_detail.html", {
        "produit": produit,
        "couleurs": couleurs
    })



from django.shortcuts import redirect
from .models import Panier, ProduitTaille, ProduitCouleur, Produit, ProduitPanier,ProduitTaille

def ajouter_au_panier(request, produit_id):
    if request.method == 'POST':
        couleur_id = request.POST.get('couleur_id')
        taille = request.POST.get('taille')
        quantite = int(request.POST.get('quantite', 1))

        produit = get_object_or_404(Produit, id=produit_id)

        if not couleur_id:
            return JsonResponse({'success': False, 'error': 'يرجى اختيار اللون'})

        # ✅ تحقق إذا فيه مقاسات متاحة (سواء كان حذاء أو حقيبة)
        has_tailles = ProduitTaille.objects.filter(couleur_id=couleur_id, stock__gt=0).exists()

        # ✅ إذا المنتج عنده مقاسات لكن المستخدم ما اختار مقاس
        if has_tailles and not taille:
            return JsonResponse({'success': False, 'error': 'يرجى اختيار المقاس'})

        couleur = get_object_or_404(ProduitCouleur, id=couleur_id)
        panier = get_or_create_panier(request)

        # ✅ تحقق إذا المنتج موجود مسبقًا بنفس اللون والمقاس
        item_qs = ProduitPanier.objects.filter(
            panier=panier,
            produit=produit,
            couleur=couleur,
            taille=taille if taille else None
        )

        if item_qs.exists():
            item = item_qs.first()
            item.quantite += quantite
            item.save()
        else:
            ProduitPanier.objects.create(
                panier=panier,
                produit=produit,
                couleur=couleur,
                taille=taille if taille else None,
                quantite=quantite
            )

        return JsonResponse({'success': True, 'nom_produit': f"{produit.categorie.nom} {produit.nom} ",})

    return JsonResponse({'success': False, 'error': 'طلب غير صالح'})




from django.template.loader import render_to_string
from django.http import HttpResponse

def cart_items_partial(request):
    panier = get_or_create_panier(request)
    cart_items = ProduitPanier.objects.filter(panier=panier)



    html = render_to_string('store/cart_items_partial.html', {
        'cart_items': cart_items,
    } ,request=request)

    return JsonResponse({'html': html, 'count': cart_items.count()})






def afficher_panier(request):
    panier = get_or_create_panier(request)
    produits = ProduitPanier.objects.filter(panier=panier) if panier else []

    # حساب إجمالي السعر لكل منتج في السلة
    total = sum(item.produit.prix * item.quantite for item in produits)

    return render(request, 'store/shoping_cart.html', {
        'produits': produits,
        'total': total,  # إرسال المجموع النهائي
        'panier': panier,
    })







@require_POST
def remove_from_cart(request, item_id):

    # نجيب المنتج داخل السلة
    item = get_object_or_404(ProduitPanier, id=item_id)
    panier = item.panier

    # نحذف المنتج فقط
    item.delete()

    # نحسب الأسعار بعد الحذف
    total_produits = sum(p.produit.prix * p.quantite for p in panier.produits.all())

    # حساب التوصيل إذا كان الزبون اختار ولاية + نوع توصيل
    type_livraison = request.POST.get("type_livraison")
    wilaya_id = request.POST.get("wilaya")
    frais_livraison = 0

    if wilaya_id and type_livraison:
        try:
            wilaya = Wilaya.objects.get(id=wilaya_id)
            if type_livraison == "bureau":
                frais_livraison = wilaya.prix_bureau or 0
            elif type_livraison == "domicile":
                frais_livraison = wilaya.prix_domicile or 0
        except Wilaya.DoesNotExist:
            frais_livraison = 0

    total_final = total_produits + frais_livraison

    # نرجع JSON بدل إعادة توجيه
    return JsonResponse({
        "success": True,
        "total_produits": f"{total_produits:.0f}",
        "frais_livraison": f"{frais_livraison:.0f}",
        "total_final": f"{total_final:.0f}",
        "count": panier.produits.count(),  # ✅ هنا الجديد

    })


from django.views.decorators.http import require_POST


@require_POST

def update_quantity(request, item_id):
    item = get_object_or_404(ProduitPanier, id=item_id)

    # قراءة الكمية الجديدة
    try:
        quantite = int(request.POST.get("quantite", item.quantite))
    except (TypeError, ValueError):
        quantite = item.quantite

    if quantite < 1:
        quantite = 1

    # تحديث الكمية
    item.quantite = quantite
    item.save()

    # السعر الجزئي لهذا المنتج
    line_total = item.quantite * item.produit.prix

    # حساب مجموع المنتجات (بدون التوصيل)
    panier = item.panier
    total_produits = sum(p.produit.prix * p.quantite for p in panier.produits.all())

    # حساب التوصيل إذا أرسل الزبون النوع والولاية
    type_livraison = request.POST.get("type_livraison")
    wilaya_id = request.POST.get("wilaya")

    frais_livraison = 0
    if wilaya_id and type_livraison:
        try:
            wilaya = Wilaya.objects.get(id=wilaya_id)
            if type_livraison == "bureau":
                frais_livraison = wilaya.prix_bureau or 0
            elif type_livraison == "domicile":
                frais_livraison = wilaya.prix_domicile or 0
        except Wilaya.DoesNotExist:
            frais_livraison = 0

    # المجموع النهائي
    total_final = total_produits + frais_livraison

    return JsonResponse({
        "success": True,
        "quantite": item.quantite,
        "line_total": f"{line_total:.0f}",
        "total_produits": f"{total_produits:.0f}",
        "frais_livraison": f"{frais_livraison:.0f}",
        "total_final": f"{total_final:.0f}",
    })




def confirmer_commande(request):
    if request.method == "POST":
        nom_complet = request.POST.get("nom")
        telephone = request.POST.get("telephone")
        wilaya_id = request.POST.get("wilaya")
        commune_id = request.POST.get("commune")
        type_livraison = request.POST.get("type_livraison")

        panier = get_or_create_panier(request)
        produits_panier = panier.produits.all()

        if not produits_panier.exists():
            return JsonResponse({"success": False, "error": "⚠️ السلة فارغة"})

        # إنشاء العميل
        client = Client.objects.create(
            nom_complet=nom_complet,
            telephone=telephone,
            wilaya_id=wilaya_id,
            commune_id=commune_id,
            type_livraison=type_livraison,
        )
        panier.client = client
        panier.save()

        # حساب الأسعار
        total_produits = 0
        line_totals = []

        for p in produits_panier:
            line_total = p.produit.prix * p.quantite
            total_produits += line_total
            line_totals.append({
                "produit": p.produit.nom,
                "quantite": p.quantite,
                "line_total": line_total
            })

        wilaya = Wilaya.objects.get(id=wilaya_id)
        frais_livraison = wilaya.prix_bureau if type_livraison == "bureau" else wilaya.prix_domicile
        frais_livraison = frais_livraison or 0

        total_final = total_produits + frais_livraison

        # إنشاء الطلبية
        commande = Commande.objects.create(
            client=client,
            panier=panier,
            total_sans_livraison=total_produits,
            total_avec_livraison=total_final,
        )

        # إنقاص الكمية من المخزون
        for item in produits_panier:
            produit_taille = ProduitTaille.objects.filter(
                couleur=item.couleur, taille=item.taille
            ).first()
            if produit_taille:
                produit_taille.stock = max(0, produit_taille.stock - item.quantite)
                if produit_taille.stock_vrai is not None:
                    produit_taille.stock_vrai = max(0, produit_taille.stock_vrai - item.quantite)
                produit_taille.save()

        # إعادة تعيين السلة
        if "panier_id" in request.session:
            del request.session["panier_id"]
        new_panier = Panier.objects.create()
        request.session["panier_id"] = new_panier.id

        return JsonResponse({
            "success": True,
            "message": "🎉 تم تسجيل طلبك بنجاح، سنتواصل معك قريباً",
            "totals": {
                "line_totals": line_totals,
                "total_produits": total_produits,
                "frais_livraison": frais_livraison,
                "total_final": total_final,
            }
        })

    return JsonResponse({"success": False, "error": "❌ طلب غير صالح"})




from django.http import JsonResponse
import re
def produits_par_etiquette(request, etiquette):
    couleurs = ProduitCouleur.objects.filter(produit__etiquette=etiquette).select_related('produit')
    return render(request, "store/product.html", {
        "couleurs": couleurs,
        "etiquette": etiquette
    })

def chaussures_promo_solde(request):
    couleurs = ProduitCouleur.objects.filter(produit__categorie__nom='Chaussures',produit__etiquette__in=['PROMO','SOLDE'])
    return render(request,"store/product.html",{"couleurs":couleurs,"promo_solde":True,"page_source":"index",})

def sacs_promo_solde(request):
    couleurs = ProduitCouleur.objects.filter(produit__categorie__nom='Sacs',produit__etiquette__in=['PROMO','SOLDE'])
    return render(request,"store/product.html",{"couleurs":couleurs,"promo_solde":True,"page_source":"index",})



def get_or_create_panier(request):
    panier_id = request.session.get('panier_id')
    if panier_id:
        try:
            return Panier.objects.get(id=panier_id)
        except Panier.DoesNotExist:
            pass
    panier = Panier.objects.create()
    request.session['panier_id'] = panier.id
    return panier


from .models import Wilaya, Commune

@never_cache
def panier_view(request):
    if not request.session.get('panier_id'):
        return redirect('home')

    panier = get_or_create_panier(request)
    produits_panier = panier.produits.all()

    wilayas = Wilaya.objects.all()
    communes = Commune.objects.all()

    total_produits = sum(item.produit.prix * item.quantite for item in produits_panier)

    wilaya = wilayas.first()
    frais_livraison = wilaya.prix_bureau if wilaya else 0
    total_final = total_produits + frais_livraison

    return render(request, 'store/shoping_cart.html', {
        'total_produits' :total_produits,
        'produits_panier': produits_panier,
        'panier': panier,
        'wilayas': wilayas,
        'communes': communes,
        'frais_livraison': frais_livraison,
        'total_final': total_final,
    })



from django.http import JsonResponse
from .models import Commune

def get_communes(request, wilaya_id):
    communes = Commune.objects.filter(wilaya_id=wilaya_id).values('id', 'nom')
    return JsonResponse({'communes': list(communes)})


def get_shipping_options(request, wilaya_id):
    try:
        wilaya = Wilaya.objects.get(id=wilaya_id)
        return JsonResponse({
            'bureau': wilaya.prix_bureau,
            'domicile': wilaya.prix_domicile
        })
    except Wilaya.DoesNotExist:
        return JsonResponse({'error': 'الولاية غير موجودة'}, status=404)



from store.models import ProduitCouleur


def liste_produits(request):
    categorie_nom = request.GET.get('categorie')

    if categorie_nom:
        couleurs = ProduitCouleur.objects.select_related('produit', 'produit__categorie') \
            .filter(produit__categorie__nom__iexact=categorie_nom) \
            .prefetch_related('images')
    else:
        couleurs = ProduitCouleur.objects.select_related('produit').prefetch_related('images')

    return render(request, 'store/product.html', {
        'couleurs': couleurs,
        'categorie_active': categorie_nom,
        "page_source": "shop",
    })


def get_categorie_nom(request):
    produit_id = request.GET.get('produit_id')
    try:
        produit = Produit.objects.select_related('categorie').get(id=produit_id)
        return JsonResponse({'categorie_nom': produit.categorie.nom})
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit introuvable'}, status=404)

def get_tailles(request, couleur_id):
    try:
        couleur = ProduitCouleur.objects.get(id=couleur_id)
        tailles = [
            {'taille': t.taille, 'stock': t.stock}
            for t in couleur.tailles.all()
        ]
        return JsonResponse({'tailles': tailles})
    except ProduitCouleur.DoesNotExist:
        return JsonResponse({'tailles': []})



def search(request):
    # 1️⃣ الحصول على الكلمات المفتاحية من شريط البحث
    query = request.GET.get("q", "").strip()
    produits = Produit.objects.all()
    couleurs = ProduitCouleur.objects.all()

    # 🧠 قاموس الألوان (فرنسية + إنجليزية)
    color_synonyms = {
        "bleu": ["bleu", "blue", "azur"],
        "noir": ["noir", "black", "dark"],
        "blanc": ["blanc", "white"],
        "rouge": ["rouge", "red", "crimson"],
        "vert": ["vert", "green"],
        "jaune": ["jaune", "yellow", "gold"],
        "beige": ["beige", "sand"],
        "marron": ["marron", "brown"],
        "gris": ["gris", "gray", "grey"],
        "rose": ["rose", "pink"],
        "violet": ["violet", "purple"],
        "orange": ["orange"],
    }

    color_words = []
    category_words = []

    # 2️⃣ معالجة النص المكتوب في البحث (q)
    if query:
        keywords = query.split()
        for word in keywords:
            w = word.lower().strip()
            found_color = False
            for base_color, synonyms in color_synonyms.items():
                if w in synonyms:
                    color_words.extend(synonyms)
                    found_color = True
                    break
            if not found_color:
                category_words.append(w)

        # فلترة حسب الاسم، الوصف، التصنيف
        for word in category_words:
            produits = produits.filter(
                Q(nom__icontains=word)
                | Q(description__icontains=word)
                | Q(categorie__nom__icontains=word)
            )

        produits = produits.distinct()

    # 3️⃣ المعطيات القادمة من واجهة الفلترة
    couleurs_from_get = request.GET.getlist("couleur")  # ألوان مختارة
    prix_min = request.GET.get("prix_min")
    prix_max = request.GET.get("prix_max")
    sort = request.GET.get("sort")

    # 🟦 تجهيز الألوان المختارة
    selected_colors = []
    for c in couleurs_from_get:
        c = c.lower().strip()
        for base, syns in color_synonyms.items():
            if c in syns:
                selected_colors.extend(syns)
                break
        else:
            selected_colors.append(c)

    # دمج كل الألوان (من البحث ومن الفلتر)
    all_colors = set(color_words + selected_colors)

    # 🟨 فلترة المنتجات حسب اللون
    if all_colors:
        color_q = Q()
        for c in all_colors:
            color_q |= Q(couleurs__couleur__icontains=c)
        produits = produits.filter(color_q).distinct()

    # 🟥 فلترة السعر
    if prix_min:
        try:
            produits = produits.filter(prix__gte=float(prix_min))
        except:
            pass
    if prix_max:
        try:
            produits = produits.filter(prix__lte=float(prix_max))
        except:
            pass

    # 🟩 الترتيب (sort)
    if sort == "price_asc":
        produits = produits.order_by("prix")
    elif sort == "price_desc":
        produits = produits.order_by("-prix")
    elif sort == "newness":
        produits = produits.order_by("-id")  # لا يوجد date_creation
    elif sort == "popularity":
        produits = produits.order_by("-vues")

    produits = produits.distinct()

    # 🟧 فلترة قائمة الألوان حسب المنتجات الناتجة
    if all_colors:
        color_filter = Q(produit__in=produits)
        cq = Q()
        for c in all_colors:
            cq |= Q(couleur__icontains=c)
        color_filter &= cq
        couleurs = ProduitCouleur.objects.filter(color_filter).distinct()
    else:
        couleurs = ProduitCouleur.objects.filter(produit__in=produits).distinct()

    # ⚠️ إذا لم يوجد أي منتج
    no_results = not couleurs.exists()

    return render(
        request,
        "store/product.html",
        {
            "couleurs": couleurs,
            "query": query,
            "no_results": no_results,
        },
    )


from django.shortcuts import render, redirect
from .forms import MessageContactForm

def contact(request):
    success_message = None  # متغير لرسالة النجاح

    if request.method == 'POST':
        form = MessageContactForm(request.POST)
        if form.is_valid():
            form.save()
            success_message = "✅ تم إرسال رسالتك بنجاح! سنقوم بالرد عليك قريبًا."
            form = MessageContactForm()  # لإفراغ الحقول بعد الإرسال
    else:
        form = MessageContactForm()

    return render(request, 'store/contact.html', {
        'form': form,
        'success_message': success_message
    })


