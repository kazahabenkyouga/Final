import os
import django
from accountbook.models import GmailTransaction  # yourappとYourModelは適宜変更

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finalproject.settings')  # 'finalproject.settings'はsettings.pyのあるパスに合わせる
django.setup()

import json


def pie_chart_month(request, year, month):
    # 例: 指定年月の取引を取得
    transactions = GmailTransaction.objects.filter(date__year=year, date__month=month)

    # 何かカテゴリー別に集計済みのlabels, data, detail_dataを作る（例）
    labels = ['未分類']  # 仮
    data = [sum(t.amount for t in transactions)]
    detail_data = [
        [{'date': t.date.strftime('%Y-%m-%d'), 'amount': t.amount} for t in transactions]
    ]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'detail_data': json.dumps(detail_data),
        'current_month': month,
        'prev_year': year,
        'prev_month': month - 1 if month > 1 else 12,
        'next_year': year,
        'next_month': month + 1 if month < 12 else 1,
    }
    print(detail_data)



pie_chart_month(5, 5, 5)

# 例えば全データを取得して表示
for obj in GmailTransaction.objects.all():
    print(obj)
