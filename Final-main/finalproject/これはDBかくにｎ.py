from accountbook.models import GmailTransaction

# 全件取得（例）
all_data = GmailTransaction.objects.all()

for item in all_data:
    print(item.usage_datetime, item.amount)
