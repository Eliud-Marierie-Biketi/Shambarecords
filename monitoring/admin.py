from django.contrib import admin

from monitoring.models import Field, FieldUpdate, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name")


class FieldUpdateInline(admin.TabularInline):
    model = FieldUpdate
    extra = 0
    readonly_fields = ("updated_by", "stage", "notes", "created_at")
    can_delete = False
    fields = readonly_fields


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "crop_type", "planting_date", "current_stage", "assigned_agent", "status_label")
    list_filter = ("current_stage", "crop_type")
    search_fields = ("name", "crop_type")
    autocomplete_fields = ("assigned_agent",)
    inlines = [FieldUpdateInline]

    @admin.display(description="Status")
    def status_label(self, obj: Field) -> str:
        return obj.status


@admin.register(FieldUpdate)
class FieldUpdateAdmin(admin.ModelAdmin):
    list_display = ("field", "updated_by", "stage", "created_at")
    list_filter = ("stage", "created_at")
    search_fields = ("field__name", "updated_by__username")
