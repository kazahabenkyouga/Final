from datetime import datetime, timedelta
from .models import GmailData
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.shortcuts import render
from .models import GmailTransaction
from calendar import monthrange
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from collections import defaultdict
import calendar
import json
from django.utils.timezone import now


##折れ線グラフの処理
def line_graph(request):
    today = now()
    current_year = today.year
    current_month = today.month

    # 月初
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
    first_day_2months_ago = (first_day_last_month - timedelta(days=1)).replace(day=1)

    # 集計対象期間：過去2ヶ月分（例：4月 + 5月）
    past_transactions = GmailTransaction.objects.filter(
        usage_datetime__gte=first_day_2months_ago,
        usage_datetime__lt=first_day_this_month
    )

    # 日にちごとのデータ格納
    from collections import defaultdict

    daily_totals = defaultdict(lambda: [0, 0])  # day: [4月分, 5月分]
    for tx in past_transactions:
        dt = tx.usage_datetime
        day = dt.day
        month = dt.month
        if month == first_day_2months_ago.month:
            daily_totals[day][0] += tx.amount
        elif month == first_day_last_month.month:
            daily_totals[day][1] += tx.amount

    # 累積平均（過去2ヶ月分）
    avg_cumulative = []
    days = list(range(1, 32))  # 1日〜31日
    cum_sum = 0
    for day in days:
        a, b = daily_totals[day]
        avg = (a + b) / 2
        cum_sum += avg
        avg_cumulative.append(round(cum_sum))

    # 今月のトランザクションから累積を作成
    current_transactions = GmailTransaction.objects.filter(
        usage_datetime__gte=first_day_this_month,
        usage_datetime__lte=today
    )

    daily_this_month = defaultdict(int)
    for tx in current_transactions:
        day = tx.usage_datetime.day
        daily_this_month[day] += tx.amount

    current_cumulative = []
    cum_sum = 0
    for day in days:
        if day > today.day:
            break
        cum_sum += daily_this_month[day]
        current_cumulative.append(cum_sum)

    context = {
        'labels': days,
        'avg_cumulative': avg_cumulative,
        'current_cumulative': current_cumulative,
        'current_month_label': today.strftime('%Y-%m')
    }
    return render(request, 'line_graph.html', context)

@csrf_exempt
def fetch_credit_info(request):
    if request.method == 'POST':
        from .quickstart import get_gmail_data_and_unclassified_items
        try:
            updated, unclassified_items = get_gmail_data_and_unclassified_items()
            message = "新しいデータを取得しました。" if updated else "最新の情報です。更新はありませんでした。"
            return JsonResponse({
                'status': 'success',
                'updated': updated,
                'message': message,
                'unclassified_items': unclassified_items
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid method'}, status=405)

# def fetch_credit_info(request):
#     if request.method == 'POST':
#         from .quickstart import get_gmail_data
#
#         try:
#             updated = get_gmail_data(request)
#
#             if updated:
#                 message = "新しいデータを取得しました。"
#             else:
#                 message = "最新の情報です。更新はありませんでした。"
#
#             # DB保存処理（必要なら）
#
#             return JsonResponse({'status': 'success', 'updated': updated, 'message': message})
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
#
#     return JsonResponse({'status': 'invalid method'}, status=405)


def monthly_summary_view(request):
    monthly_data = (
        GmailTransaction.objects
        .annotate(month=TruncMonth('usage_datetime'))
        .values('month')
        .annotate(total_amount=Sum('amount'))
        .order_by('month')
    )
    return render(request, 'accountbook/monthly_summary.html', {'monthly_data': monthly_data})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import GmailTransaction
from collections import defaultdict

@csrf_exempt
def update_categories(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            updates = data.get('updates', [])

            for item in updates:
                obj_id = item.get('id')
                new_category = item.get('category')

                # データを取得して更新
                obj = GmailTransaction.objects.get(id=obj_id)
                # obj.tag = item["tag"]
                obj.tag = item.get("tag", "")  # ← ここを修正
                obj.category = new_category
                obj.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def pie_chart_details(request, year, month):
    category = request.GET.get('category')
    if not category:
        return JsonResponse({'error': 'カテゴリが指定されていません'}, status=400)

    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    transactions = GmailTransaction.objects.filter(
        usage_datetime__range=(start_date, end_date),
        category=category
    ).values('usage_datetime', 'amount').order_by('usage_datetime')

    details = [
        {
            'date': t['usage_datetime'].strftime('%Y-%m-%d'),
            'amount': t['amount']
        } for t in transactions
    ]

    return JsonResponse({'details': details})

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

    start_date = current_date
    end_date = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    transactions = GmailTransaction.objects.filter(usage_datetime__range=(start_date, end_date))

    data_dict = {}
    for t in transactions:
        category = getattr(t, 'category', '未分類')
        data_dict[category] = data_dict.get(category, 0) + t.amount

    labels = list(data_dict.keys())
    data = list(data_dict.values())
    # タグごとの集計
    tag_data_dict = {}
    for t in transactions:
        tag = t.tag if t.tag else 'タグなし'
        tag_data_dict[tag] = tag_data_dict.get(tag, 0) + t.amount

    tag_labels = list(tag_data_dict.keys())
    tag_values = list(tag_data_dict.values())

    # 明細用のリストを作成（取引日付と金額など）
    categories = ["未分類","外食費", "交通費", "食費", "交際費", "その他", "日用品", "趣味", "本"]
    details = [
        {
            'id': t.id,
            'date': t.usage_datetime.strftime('%Y-%m-%d'),
            'category': getattr(t, 'category', '未分類'),
            'amount': t.amount,
            'tag': t.tag,
            # 必要なら他のフィールドも追加
        }
        for t in transactions.order_by('usage_datetime')
    ]
    total_amount = sum(data)
    context = {
        'current_year': current_date.year,
        'current_month': current_date.month,
        'prev_year': prev_date.year,
        'prev_month': prev_date.month,
        'next_year': next_date.year,
        'next_month': next_date.month,
        'labels': labels,
        'data': data,
        'details': details,
        'categories':categories,
        'total_amount': total_amount,

        # これをテンプレートに渡す
        'tag_labels': tag_labels,
        'tag_values': tag_values,
    }
    return render(request, 'pie_chart.html', context)



def hello_view(request):
    return render(request, 'hello.html')


import json


def transactions_by_month(request, year, month):
    # yearとmonthでフィルタリング
    transactions = GmailTransaction.objects.filter(
        usage_datetime__year=year,
        usage_datetime__month=month
    ).order_by('usage_datetime')

    # 合計金額も計算（必要なら）
    total_amount = sum(

        t.amount for t in transactions)

    context = {
        'transactions': transactions,
        'year': year,
        'month': month,
        'total_amount': total_amount,
    }
    return render(request, 'accountbook/transactions_by_month.html', context)


def check_latest_uncategorized(request):
    latest = GmailTransaction.objects.filter(category='未分類').order_by('-usage_datetime').first()
    if latest:
        data = {
            'id': latest.id,
            'usage_datetime': latest.usage_datetime.strftime('%Y/%m/%d %H:%M'),
            'amount': latest.amount,
            'category': latest.category,
            'has_uncategorized': True,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'has_uncategorized': False})

# def your_view(request):
#     # 例：ログインユーザーの明細を取得（必要に応じて条件追加）
#     details = GmailTransaction.objects.filter(user=request.user)
#
#     # カテゴリー別合計
#     category_totals = defaultdict(int)
#     tag_totals = defaultdict(int)
#     print('category_totals:', dict(category_totals))
#     print('tag_totals:', dict(tag_totals))
#     for item in details:
#         # カテゴリー別集計
#         if item.category:
#             category_totals[item.category] += item.amount
#
#         # タグ別集計
#         if item.tag:
#             tag_totals[item.tag] += item.amount
#
#     context = {
#         'details': details,
#         'categories': ["未分類","外食費", "交通費", "食費", "交際費", "その他", "日用品", "趣味", "本"], # カテゴリーリスト
#         'labels': list(category_totals.keys()),
#         'data': list(category_totals.values()),
#         'tag_labels': list(tag_totals.keys()),
#         'tag_values': list(tag_totals.values()),
#     }
#
#     return render(request, 'pie_chart.html', context)