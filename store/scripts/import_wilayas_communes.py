import sys
from django.apps import apps
Wilaya = apps.get_model('store', 'Wilaya')
Commune = apps.get_model('store', 'Commune')

# ✅ لا تنفذ أي شيء أثناء التهيئة أو الترحيل
if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
    exit()

import csv
from store.models import Wilaya, Commune


with open('store/data/wilayas_communes.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        wilaya_nom = row["wilaya_name"].strip()
        commune_nom = row["commune_name"].strip()

        wilaya, _ = Wilaya.objects.get_or_create(
            nom=wilaya_nom,
            defaults={'prix_bureau': 0, 'prix_domicile': 0}
        )

        Commune.objects.get_or_create(
        nom=commune_nom,
        wilaya=wilaya
        )


print("✅ تم استيراد الولايات والبلديات.")
