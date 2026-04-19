from django.urls import path

from monitoring import views

urlpatterns = [
    path("dashboard/admin/", views.admin_dashboard, name="admin-dashboard"),
    path("dashboard/agent/", views.agent_dashboard, name="agent-dashboard"),
    path("fields/", views.field_list, name="field-list"),
    path("fields/add/", views.field_create, name="field-create"),
    path("fields/<int:pk>/", views.field_detail, name="field-detail"),
    path("fields/<int:pk>/edit/", views.field_edit, name="field-edit"),
    path("fields/<int:pk>/update-stage/", views.field_update_stage, name="field-update-stage"),
]
