from django.urls import path
from . import views

# urls.py
urlpatterns = [
    path('pie/', views.pie_chart, name='pie_chart_current'),  # 今月など引数なし用
    path('pie/<int:year>/<int:month>/', views.pie_chart, name='pie_chart_month'),
    path('pie/<int:year>/<int:month>/details/', views.pie_chart_details, name='pie_chart_details'),
    path('fetch-credit-info/', views.fetch_credit_info, name='fetch_credit_info'),
    path('update_categories/', views.update_categories, name='update_categories'),
    path('check_latest_uncategorized/', views.check_latest_uncategorized, name='check_latest_uncategorized'),
    path('line-graph/', views.line_graph, name='line_graph'),

]

