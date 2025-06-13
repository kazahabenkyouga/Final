from datetime import datetime, timedelta
from .models import GmailData
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.shortcuts import render
from .models import GmailTransaction
from calendar import monthrange
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def fetch_credit_info(request):
    if request.method == 'POST':
        from .quickstart import get_gmail_data

        try:
            card_info_list = get_gmail_data(request)

            # DB保存処理（必要なら）

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'invalid method'}, status=405)


def monthly_summary_view(request):
    monthly_data = (
        GmailTransaction.objects
        .annotate(month=TruncMonth('usage_datetime'))
        .values('month')
        .annotate(total_amount=Sum('amount'))
        .order_by('month')
    )
    return render(request, 'accountbook/monthly_summary.html', {'monthly_data': monthly_data})


def save_gmail_data_to_db(year, month, labels, counts):
    for label, count in zip(labels, counts):
        GmailData.objects.update_or_create(
            label=label,
            year=year,
            month=month,
            defaults={'count': count}
        )

def pie_chart(request, year=None, month=None):
    today = datetime.today()
    if year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    current_date = datetime(year, month, 1)
    prev_date = current_date - timedelta(days=1)
    next_date = (current_date + timedelta(days=31)).replace(day=1)

    # 日付範囲を設定
    start_date = current_date
    end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    # データ取得・集計
    transactions = GmailTransaction.objects.filter(usage_datetime__range=(start_date, end_date))
    data_dict = {}
    for t in transactions:
        category = getattr(t, 'category', '未分類')
        data_dict[category] = data_dict.get(category, 0) + t.amount

    labels = list(data_dict.keys())
    data = list(data_dict.values())

    context = {
        'current_year': current_date.year,
        'current_month': current_date.month,
        'prev_year': prev_date.year,
        'prev_month': prev_date.month,
        'next_year': next_date.year,
        'next_month': next_date.month,
        'labels': labels,
        'data': data,
    }
    return render(request, 'pie_chart.html', context)


def hello_view(request):
    return render(request, 'hello.html')

