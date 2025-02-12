from django.urls import path
from . import views

urlpatterns = [
    path('', views.analysis_dashboard, name='analysis_dashboard'),  # Главная страница анализа
    path('<int:table_id>/', views.table_analysis, name='table_analysis'),  # Анализ конкретной таблицы
    path('update-row/<int:row_id>/', views.update_row, name='update_row'),
]
