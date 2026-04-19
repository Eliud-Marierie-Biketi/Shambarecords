from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from monitoring.forms import FieldForm, FieldStageUpdateForm
from monitoring.models import Field, FieldUpdate, User


def _is_admin(user: User) -> bool:
    return user.is_authenticated and (user.is_staff or user.role == User.Role.ADMIN)


def _field_queryset_for_user(user: User):
    if _is_admin(user):
        return Field.objects.select_related("assigned_agent").prefetch_related("updates")
    return Field.objects.select_related("assigned_agent").prefetch_related("updates").filter(assigned_agent=user)


@login_required
def dashboard_redirect(request):
    if _is_admin(request.user):
        return redirect("admin-dashboard")
    return redirect("agent-dashboard")


@login_required
def admin_dashboard(request):
    if not _is_admin(request.user):
        return redirect("agent-dashboard")

    fields = _field_queryset_for_user(request.user)
    status_counts = {"Active": 0, "At Risk": 0, "Completed": 0}
    stage_counts = {label: 0 for label, _ in Field.Stage.choices}
    for field in fields:
        status_counts[field.status] = status_counts.get(field.status, 0) + 1
        stage_counts[field.current_stage] = stage_counts.get(field.current_stage, 0) + 1
    recent_updates = FieldUpdate.objects.select_related("field", "updated_by").all()[:8]
    assigned_breakdown = (
        Field.objects.filter(assigned_agent__isnull=False)
        .values("assigned_agent__username", "assigned_agent__first_name", "assigned_agent__last_name")
        .annotate(total=Count("id"))
        .order_by("-total", "assigned_agent__username")
    )

    context = {
        "fields": fields,
        "total_fields": fields.count(),
        "active_count": status_counts.get("Active", 0),
        "at_risk_count": status_counts.get("At Risk", 0),
        "completed_count": status_counts.get("Completed", 0),
        "stage_counts": stage_counts,
        "recent_updates": recent_updates,
        "assigned_breakdown": assigned_breakdown,
    }
    return render(request, "dashboard_admin.html", context)


@login_required
def agent_dashboard(request):
    if _is_admin(request.user):
        return redirect("admin-dashboard")

    fields = _field_queryset_for_user(request.user)
    status_counts = {"Active": 0, "At Risk": 0, "Completed": 0}
    for field in fields:
        status_counts[field.status] = status_counts.get(field.status, 0) + 1
    recent_updates = FieldUpdate.objects.filter(updated_by=request.user).select_related("field").all()[:6]

    return render(
        request,
        "dashboard_agent.html",
        {
            "fields": fields,
            "total_fields": fields.count(),
            "active_count": status_counts.get("Active", 0),
            "at_risk_count": status_counts.get("At Risk", 0),
            "completed_count": status_counts.get("Completed", 0),
            "recent_updates": recent_updates,
        },
    )


@login_required
def field_list(request):
    fields = _field_queryset_for_user(request.user)
    return render(request, "field_list.html", {"fields": fields, "is_admin": _is_admin(request.user)})


@login_required
def field_detail(request, pk: int):
    queryset = _field_queryset_for_user(request.user)
    field = get_object_or_404(queryset, pk=pk)
    return render(
        request,
        "field_detail.html",
        {
            "field": field,
            "updates": field.updates.select_related("updated_by").all(),
            "can_edit": _is_admin(request.user),
            "can_update_stage": _is_admin(request.user) or field.assigned_agent_id == request.user.id,
        },
    )


@login_required
def field_create(request):
    if not _is_admin(request.user):
        return redirect("agent-dashboard")

    if request.method == "POST":
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Field created successfully.")
            return redirect("field-list")
    else:
        form = FieldForm()
    return render(request, "field_form.html", {"form": form, "title": "Create Field"})


@login_required
def field_edit(request, pk: int):
    if not _is_admin(request.user):
        return redirect("agent-dashboard")

    field = get_object_or_404(Field, pk=pk)
    if request.method == "POST":
        form = FieldForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, "Field updated successfully.")
            return redirect("field-detail", pk=field.pk)
    else:
        form = FieldForm(instance=field)
    return render(request, "field_form.html", {"form": form, "title": "Edit Field"})


@login_required
def field_update_stage(request, pk: int):
    field = get_object_or_404(_field_queryset_for_user(request.user), pk=pk)
    if not (_is_admin(request.user) or field.assigned_agent_id == request.user.id):
        return redirect("dashboard")

    if request.method == "POST":
        form = FieldStageUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.field = field
            update.updated_by = request.user
            update.save()
            field.current_stage = update.stage
            field.save(update_fields=["current_stage", "updated_at"])
            messages.success(request, "Field stage updated.")
            return redirect("field-detail", pk=field.pk)
    else:
        form = FieldStageUpdateForm(initial={"stage": field.current_stage})
    return render(request, "field_update_form.html", {"form": form, "field": field})
