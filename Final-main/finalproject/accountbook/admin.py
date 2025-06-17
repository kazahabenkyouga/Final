from django.contrib import admin
from .models import GmailTransaction # モデル名をインポート

admin.site.register(GmailTransaction)  # 管理画面に登録
