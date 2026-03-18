from django.urls import path
from . import views
from .presentation_views import presentation_view

urlpatterns = [
    path('wqmap/', views.deffeyes_chart_view, name='deffeyes_chart'),
    path('presentation/', presentation_view, name='presentation'),
    path('api/deffeyes-data/', views.deffeyes_data_api, name='deffeyes_data'),
    path('api/deffeyes-light/', views.light_update_api, name='deffeyes_light'),
    path('api/deffeyes-adjust/', views.adjust_api, name='deffeyes_adjust'),
    path('api/system/save/', views.system_save_api, name='system_save'),
    path('api/system/list/', views.system_list_api, name='system_list'),
    path('api/system/<int:sys_id>/load/', views.system_load_api, name='system_load'),
    path('api/system/<int:sys_id>/delete/', views.system_delete_api, name='system_delete'),
    path('wqmap/multi/<int:count>/', views.multi_chart_view, name='multi_chart'),
]
