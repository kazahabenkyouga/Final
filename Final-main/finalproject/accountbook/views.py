from django.shortcuts import render
from datetime import datetime, timedelta
from .models import GmailData

def save_gmail_data_to_db(year, month, labels, counts):
    for label, count in zip(labels, counts):
        GmailData.objects.update_or_create(
            label=label,
            year=year,
            month=month,
            defaults={'count': count}
        )

def pie_chart(request, year=None, month=None):
    from datetime import datetime, timedelta

    today = datetime.today()
    if year is None or month is None:
        year = today.year
        month = today.month
    else:
        year = int(year)
        month = int(month)

    current_date = datetime(year, month, 1)
    prev_date = current_date - timedelta(days=1)
    if month == 12:
        next_date = datetime(year + 1, 1, 1)
    else:
        next_date = datetime(year, month + 1, 1)
    labels = ['A', 'B', 'C']
    data = [30, 45, 25]

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

