import random
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Case, CaseItem, OpenHistory, Profile


# Bosh sahifa (Keyslar ro'yxati)
def index(request):
  cases = Case.objects.all()
  return render(request, 'index.html', {'cases': cases})


# Keys ochish funksiyasi (AJAX orqali ishlaydi)
@login_required
def open_case(request, case_id):
  if request.method == 'POST':
    case = get_object_or_404(Case, id=case_id)
    profile, created = Profile.objects.get_or_create(user=request.user)

    # 1. Foydalanuvchi balansini tekshirish
    if profile.balance < case.price:
      return JsonResponse(
          {'success': False, 'error': "Balansingizda yetarli mablag' yo'q!"}
      )

    # 2. Keys ichidagi buyumlar va ularning ehtimolligini olish
    case_items = CaseItem.objects.filter(case=case)
    if not case_items.exists():
      return JsonResponse(
          {'success': False, 'error': "Bu keysda hozircha buyumlar yo'q!"}
      )

    items = [ci.item for ci in case_items]
    chances = [
        ci.chance for ci in case_items
    ]  # Masalan: [70.0, 25.0, 4.0, 1.0]

    # 3. Balansdan pulni ayirish
    profile.balance -= case.price
    profile.save()

    # 4. Ehtimollik bo'yicha tasodifiy item tanlash (Weighted Random)
    chosen_item = random.choices(items, weights=chances, k=1)[0]

    # 5. Tarixga saqlash (Oxirgi yutuqlar uchun)
    OpenHistory.objects.create(
        user=request.user, case=case, item=chosen_item
    )

    # 6. Frontendga natijani JSON ko'rinishida qaytarish
    return JsonResponse({
        'success': True,
        'item_name': chosen_item.name,
        'item_image': chosen_item.image.url,
        'item_price': str(chosen_item.price),
        'rarity': chosen_item.rarity,
        'new_balance': str(profile.balance),
    })

  return JsonResponse({'success': False, 'error': 'Noto`g`ri so`rov'})