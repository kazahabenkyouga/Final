from django.urls import path
from . import views

# urls.py
urlpatterns = [
    path('pie/', views.pie_chart, name='pie_chart_current'),  # 今月など引数なし用
    path('pie/<int:year>/<int:month>/', views.pie_chart, name='pie_chart_month'),
    path('', views.hello),# 年月指定用
]

