from django.contrib import admin,messages
from django.contrib.admin import ModelAdmin
from django.core.exceptions import ValidationError
from django.utils.html import format_html_join, format_html
from decimal import Decimal
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Sum
# Register your models here.,client
from .models import Produit, Categorie, Wilaya, Commune, Client, Panier, ProduitPanier, ProduitImage, ProduitTaille, \
    ProduitCouleur, Commande, MessageContact, SOURCE_CHOICES
from .views import afficher_panier


# Register your models here.
class CategorieConfig (ModelAdmin):
    list_filter = ['nom']
    list_display = ['nom']

class ProduitImageInline(admin.TabularInline):
    model = ProduitImage
    extra = 1


from django import forms

# قائمة المقاسات و الأحجام
CHOICES_POINTURES = ['36', '37', '38', '39', '40', '41']
CHOICES_TAILLES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']


class ProduitTailleInlineForm(forms.ModelForm):
    class Meta:
        model = ProduitTaille
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        produit = None

        # نحصل على المنتج من خلال اللون المرتبط
        if self.instance.pk and self.instance.couleur and self.instance.couleur.produit:
            produit = self.instance.couleur.produit

        if produit and produit.categorie:
            categorie_nom = produit.categorie.nom.strip().lower()

            # ⚙️ المقاسات حسب نوع المنتج
            if categorie_nom == "sacs":  # ✅ إذا كانت حقيبة
                tailles_possibles = ['XS',"S", "M", "L", 'XL', 'XXL']
            elif categorie_nom == "chaussures":  # ✅ إذا كان حذاء
                tailles_possibles = ["36", "37", "38", "39", "40", "41", "42"]
            else:
                tailles_possibles = []  # أي فئة أخرى

            # نحدث قائمة الخيارات
            self.fields['taille'].widget.choices = [(t, t) for t in tailles_possibles]


class ProduitTailleInline(admin.TabularInline):
    model = ProduitTaille
    form = ProduitTailleInlineForm
    extra = 1







class ProduitCouleurAdmin(admin.ModelAdmin):
    inlines = [ProduitImageInline,ProduitTailleInline]
    list_display = ['produit','couleur']
    list_filter = ['produit__categorie','produit']




class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        etiquette = cleaned_data.get("etiquette")
        prix_promo = cleaned_data.get("prix_promo")

        if etiquette in ["promo", "solde"] and not prix_promo:
            raise ValidationError({"prix_promo": "❌ يجب إدخال السعر الجديد عند اختيار Promo أو Solde."})

        return cleaned_data

class ProduitConfig (ModelAdmin):
    form = ProduitForm
    list_display = ['categorie','nom','description','prix','etiquette','prix_promo','vues','benefice','total_stock_initial','total_stock_vrai','stock_restante','quantite_vendue','benefice_total_vendu']
    list_filter = ['categorie', 'prix']


    def total_stock_vrai(self, obj):
        # نحسب مجموع stock_vrai لجميع الألوان/المقاسات المرتبطة بالمنتج
        return sum(
            taille.stock_vrai or 0
            for couleur in obj.couleurs.all()
            for taille in couleur.tailles.all()
        )

    total_stock_vrai.short_description = "Stock aprés commandé"

    def total_stock_initial(self, obj):
        # نحسب مجموع كل stock (الكمية الأصلية) لجميع الألوان والمقاسات المرتبطة بالمنتج
        return sum(
            taille.stock_initial or 0
            for couleur in obj.couleurs.all()
            for taille in couleur.tailles.all()
        )

    total_stock_initial.short_description = "Stock Initiale"

    def quantite_vendue(self, obj):
        """
        تحسب كمية المنتج التي تم بيعها
        """
        total_initial = self.total_stock_initial(obj)  # استدعاء دالة admin وليس حقل موديل
        vendue = total_initial - obj.stock_restante
        return vendue if vendue >= 0 else 0

    quantite_vendue.short_description = "كمية مباعة"

    def benefice_total_vendu(self, obj):
        """
        حساب الفائدة الإجمالية من المنتجات المباعة
        """
        total_initial = self.total_stock_initial(obj)
        quantite_vendue = total_initial - obj.stock_restante

        # استخراج الفائدة للمنتج الواحد (prix - prix_achat)
        benefice_unitaire = obj.prix - obj.prix_achat

        benefice_total = quantite_vendue * benefice_unitaire
        return f"{benefice_total} DA"


    benefice_total_vendu.short_description = "💰 فائدة المبيعات"

class WilayaConfig (ModelAdmin):
    list_filter = ['nom','prix_bureau','prix_domicile']
    list_display = ['nom','prix_bureau','prix_domicile']


class CommuneConfig (ModelAdmin):
    list_filter = ['nom','wilaya']
    list_display = ['nom','wilaya']


class ClientConfig (ModelAdmin):
    list_filter = ['nom_complet','telephone','wilaya','commune','type_livraison']
    list_display = ['nom_complet','telephone','wilaya','commune','type_livraison']


class PanierConfig (ModelAdmin):
    list_filter = ['client','date_creation']
    list_display = ['id', 'client','date_creation']


class ProduitPanierConfig(ModelAdmin):
    list_display = ['id', 'panier', 'produit', 'afficher_couleur', 'afficher_taille', 'quantite']

    def afficher_couleur(self, obj):
        try:
            return obj.couleur.couleur if obj.couleur else "—"
        except:
            return "—"
    afficher_couleur.short_description = "اللون"

    def afficher_taille(self, obj):
        try:
            return obj.taille.taille if obj.taille else "—"
        except:
            return "—"
    afficher_taille.short_description = "المقاس"



class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'produits_commande',
        'client',
        'telephone',
        'commune',
        'get_livraison_info',
        'total_avec_livraison',
        'date_commande',
        'statut',  # يجب أن يكون هنا، ولكن ليس في أول العمود
        'colored_source',
        'benifice_total',

    )
    list_editable = ('statut',)  # ✅ يسمح بالتعديل مباشرة من الجدول
    list_filter = ('date_commande', 'statut', 'client__type_livraison', 'source')
    list_display_links = ('id', 'client')
    search_fields = ['client__nom_complet', 'client__telephone','client__wilaya__nom','panier__produits__produit__nom']

    def save_model(self, request, obj, form, change):
        obj.save()

    def benifice_total(self, obj):
        total = Decimal('0')
        for item in obj.panier.produits.all():
            produit = item.produit
            if produit.prix and produit.prix_achat:
                total += (Decimal(produit.prix) - Decimal(produit.prix_achat)) * item.quantite
        return f"{total} DA"

    benifice_total.short_description = "الفائدة الإجمالية"

    # ✅ الأعمدة المهمة فقط (العرض المختصر)
    basic_fields = ['id','produits_commande', 'client','telephone','commune','get_livraison_info', 'total_avec_livraison','statut','date_commande' ]

    # ✅ الأعمدة الكاملة (التفاصيل)
    detailed_fields = list_display

    def get_list_display(self, request):
        show_all = request.session.get('show_all_mode', False)
        return self.detailed_fields if show_all else self.basic_fields

    def changelist_view(self, request, extra_context=None):
        # 🔁 التبديل بين الوضعين عند الضغط على الزر
        if request.GET.get('toggle_mode') == '1':
            current = request.session.get('show_all_mode', False)
            request.session['show_all_mode'] = not current

        # 🔹 عرض الصفحة العادية
        response = super().changelist_view(request, extra_context)

        # 🔢 حساب مجموع الفوائد حسب الطلبات الظاهرة
        total_benefice = Decimal('0')
        try:
            qs = response.context_data['cl'].queryset
            for c in qs:
                for item in c.panier.produits.all():
                    produit = item.produit
                    if produit.prix and produit.prix_achat:
                        total_benefice += (Decimal(produit.prix) - Decimal(produit.prix_achat)) * item.quantite
        except Exception as e:
            print("Erreur:", e)

        # 🔘 نص الزر
        show_all = request.session.get('show_all_mode', False)
        toggle_label = "🔙 عرض مختصر" if show_all else "🔍 عرض التفاصيل"
        toggle_url = f"{request.path}?toggle_mode=1"

        # 🎨 المربع الأخضر والزر في الأعلى
        header_html = f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin:10px 0;">
            <a href='{toggle_url}'
               style='background-color:#4CAF50;color:white;padding:8px 14px;
                      border-radius:6px;text-decoration:none;font-weight:bold;'>
               {toggle_label}
            </a>
            <div style="
                background-color:#f0fff0;
                border:2px solid #4CAF50;
                border-radius:10px;
                padding:10px 20px;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                font-weight:bold;
                color:#2e7d32;">
                💰 Total: <span style='color:#1b5e20;'>{total_benefice} DA</span>
            </div>
        </div>
        """

        # 🧩 نعرضه داخل العنوان
        if hasattr(response, 'context_data') and response.context_data:
            existing_title = response.context_data.get('title', '')
            response.context_data['title'] = mark_safe(header_html + existing_title)

        return response

    change_list_template = "admin/change_list.html"

    def colored_source(self, obj):
        colors = {
            'site': '#FF0000',
            'messages_site': '#FFA500',
            'facebook': '#4CAF50',
        }
        color = colors.get(obj.source, '#999')
        label = dict(SOURCE_CHOICES).get(obj.source, obj.source)

        return format_html(
            '<span style="display:inline-flex; align-items:center;">'
            '<span style="width:12px; height:12px; border-radius:50%; background-color:{}; '
            'display:inline-block; margin-right:6px;"></span>'
            '<span>{}</span>'
            '</span>',
            color,
            label
        )

    colored_source.short_description = 'مصدر الطلبية'

    def get_livraison_info(self, obj):
        type_livraison = obj.client.type_livraison
        wilaya = obj.client.wilaya

        if type_livraison == 'bureau':
            prix = wilaya.prix_bureau
        elif type_livraison == 'domicile':
            prix = wilaya.prix_domicile
        else:
            prix = 'غير محدد'

        return format_html("<strong>{}</strong><br><span>{} DA</span>", type_livraison, prix)

    get_livraison_info.short_description = "التوصيل"

    def telephone(self, obj):
        numero = obj.client.telephone
        if numero and len(numero) == 10:
            return '.'.join([numero[i:i + 2] for i in range(0, 10, 2)])
        return numero

    def wilaya(self, obj):
        return obj.client.wilaya

    def commune(self, obj):
        return obj.client.commune

    def type_livraison(self, obj):
        return obj.client.type_livraison

    def produits_commande(self, obj):
        lignes = []
        for i, item in enumerate(obj.panier.produits.all(), start=1):
            nom = item.produit.nom
            couleur_nom = item.couleur.couleur if item.couleur else "بدون لون"
            couleur_code = item.couleur.code if hasattr(item.couleur, 'code') and item.couleur.code else "#000"
            taille = item.taille if item.taille else "بدون مقاس"
            quantite = item.quantite

            ligne = format_html(
                '<div style="font-size:14px; white-space:nowrap; margin-bottom:3px;">'
                '<span style="color:brown; font-weight:bold;">{}) </span>'
                '<span style="color:#1a237e; font-weight:900;">{}</span>'  # الاسم
                ' - '
                '<span style="color:#1a237e; font-weight:900;">{}</span>'  # المقاس
                ' / '
                '<span style="font-weight:bold; color:{};">{}</span>'  # اللون
                ' (×{})'
                '</div>',
                i, nom, taille, couleur_code, couleur_nom, quantite
            )

            lignes.append(ligne)

        return format_html("".join(lignes))

    produits_commande.short_description = "المنتجات المطلوبة"



from decimal import Decimal
from collections import defaultdict
from django.utils import timezone
from .models import Commande, BeneficeMensuel

@admin.register(BeneficeMensuel)
class BeneficeMensuelAdmin(admin.ModelAdmin):
    list_display = ('mois', 'total_benefice','perte_retours', 'benefice_net',  'date_maj')

    def changelist_view(self, request, extra_context=None):
        # 🧮 نحسب مجموع الفوائد لكل شهر من الطلبات الموجودة
        monthly_benef = defaultdict(Decimal)
        for c in Commande.objects.all():
            # فقط الطلبيات المسلمة (livré)
            if c.statut == 'livré' and c.date_commande:
                month_name = c.date_commande.strftime('%B %Y')
                total = Decimal('0')
                for item in c.panier.produits.all():
                    produit = item.produit
                    if produit.prix and produit.prix_achat:
                        total += (Decimal(produit.prix) - Decimal(produit.prix_achat)) * item.quantite
                monthly_benef[month_name] += total

        # 🧾 نحذف القديم وننشئ الجديد
        BeneficeMensuel.objects.all().delete()
        for mois, total in monthly_benef.items():
            BeneficeMensuel.objects.create(mois=mois, total_benefice=total)

        return super().changelist_view(request, extra_context)

    def perte_retours(self, obj):
        """إظهار خسارة المرتجعات من جدول RetourMensuel"""
        from .models import RetourMensuel
        try:
            retour = RetourMensuel.objects.get(mois=obj.mois)
            total_retours = retour.total_retour + retour.total_retournee
            perte = total_retours * 150
            return f"{perte} DA"
        except RetourMensuel.DoesNotExist:
            return "0 DA"
    perte_retours.short_description = "💸 خسارة المرتجعات"

    def benefice_net(self, obj):
        """طرح خسارة المرتجعات من الفائدة الشهرية"""
        from .models import RetourMensuel
        try:
            retour = RetourMensuel.objects.get(mois=obj.mois)
            total_retours = retour.total_retour + retour.total_retournee
            perte = total_retours * 150
            benefice = obj.total_benefice - perte
            return f"{benefice} DA"
        except RetourMensuel.DoesNotExist:
            return f"{obj.total_benefice} DA"
    benefice_net.short_description = "📈 الفائدة الصافية"


from .models import RetourMensuel

@admin.register(RetourMensuel)
class RetourMensuelAdmin(admin.ModelAdmin):
    list_display = ('mois', 'lien_retour', 'lien_retournee', 'total_general', 'perte_totale', 'date_maj')

    def total_general(self, obj):
        return obj.total_retour + obj.total_retournee
    total_general.short_description = "Total retour"

    def lien_retour(self, obj):
        url = f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/?statut=retour"
        return format_html(f'<a href="{url}">{obj.total_retour}</a>')

    def lien_retournee(self, obj):
        url = f"/admin/{obj._meta.app_label}/{obj._meta.model_name}/?statut=retournée"
        return format_html(f'<a href="{url}">{obj.total_retournee}</a>')

    def get_month_number(self, mois):
        """تحويل اسم الشهر إلى رقم"""
        import calendar
        mois_nom = mois.split()[0]
        try:
            return list(calendar.month_name).index(mois_nom)
        except ValueError:
            return None

    def changelist_view(self, request, extra_context=None):
        monthly_retour = defaultdict(lambda: {'retour': 0, 'retournee': 0})
        for c in Commande.objects.all():
            if c.date_commande:
                mois = c.date_commande.strftime('%B %Y')
                if c.statut == 'retour':
                    monthly_retour[mois]['retour'] += 1
                elif c.statut == 'retournée':
                    monthly_retour[mois]['retournee'] += 1

        # نحذف القديم ونضيف الجديد
        RetourMensuel.objects.all().delete()
        for mois, data in monthly_retour.items():
            RetourMensuel.objects.create(
                mois=mois,
                total_retour=data['retour'],
                total_retournee=data['retournee']
            )

        return super().changelist_view(request, extra_context)

    def perte_totale(self, obj):
        """💸 خسارة المرتجعات الشهرية (150 DA لكل مرتجع)"""
        total_retours = obj.total_retour + obj.total_retournee
        perte = total_retours * 150
        return f"{perte:,} DA"  # منسقة بفواصل
    perte_totale.short_description = "💸 خسارة المرتجعات"



class MessageContactAdmin(admin.ModelAdmin):
    list_display = ("nom", "telephone", "message", "date")
    search_fields = ("nom", "telephone")
    list_filter = ("date",)



from django.contrib import admin
from django.db.models import Sum
from .models import Depense

@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('date','nom', 'type', 'montant', 'note')
    search_fields = ('nom',)
    list_filter = ('date','type')

    # نحدد قالب مخصص لقائمة التغيير (change list)
    change_list_template = "admin/depense_change_list.html"

    def changelist_view(self, request, extra_context=None):
        # نأخذ الاستجابة العادية أولاً
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            # queryset الناتج من صفحة الـ changelist (يحترم الفلاتر)
            qs = response.context_data['cl'].queryset
            total = qs.aggregate(total=Sum('montant'))['total'] or 0
            # نمرّر المتغيّر إلى قالب الـ admin
            response.context_data['total_depenses'] = total
        except Exception:
            # إذا لم يتوفّر شيء (مثلاً خطأ)، لا نكسر الصفحة
            response.context_data['total_depenses'] = 0

        return response


admin.site.register(Client)
admin.site.register(MessageContact,MessageContactAdmin)


admin.site.register(ProduitPanier,ProduitPanierConfig)
admin.site.register(Commande, CommandeAdmin)





admin.site.register(Categorie,CategorieConfig)
admin.site.register(Produit,ProduitConfig)
admin.site.register(Wilaya,WilayaConfig)
admin.site.register(Commune,CommuneConfig)

admin.site.register(Panier,PanierConfig)

admin.site.register(ProduitCouleur,ProduitCouleurAdmin)
admin.site.register(ProduitTaille)






