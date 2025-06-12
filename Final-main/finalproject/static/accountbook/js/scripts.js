from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # AjaxでCSRFトークンを正しく送れば外してもOK
def fetch_credit_info(request):
    if request.method == 'POST':
        # ここでGmail APIからクレジットカード情報取得の関数を呼ぶ
        from .quickstart import get_gmail_data  # 例: API取得関数

        try:
            card_info_list = get_gmail_data()

            # DB保存処理をここで実装
            for info in card_info_list:
                # 例: YourModel.objects.update_or_create(...)
                pass

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=405)
