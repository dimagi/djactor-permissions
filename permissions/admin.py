from django.contrib import admin

from permissions.models import ObjectPermission
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display=('role','permission','content_type', 'content')
    list_filter = ('role','permission','content_type')
admin.site.register(ObjectPermission, ObjectPermissionAdmin)

from permissions.models import Permission
class PermissionAdmin(admin.ModelAdmin):
    list_display=('name','codename',)
admin.site.register(Permission, PermissionAdmin)

from permissions.models import Role
class RoleAdmin(admin.ModelAdmin):
    list_display=('name',)
admin.site.register(Role, RoleAdmin)

from permissions.models import PrincipalRoleRelation
class PrincipalRoleRelationAdmin(admin.ModelAdmin):
    list_display=('actor','group', 'role', 'content')
    list_filter=('actor','group','role')
admin.site.register(PrincipalRoleRelation, PrincipalRoleRelationAdmin)


from permissions.models import ActorGroup
admin.site.register(ActorGroup)


from permissions.models import Actor
class ActorAdmin(admin.ModelAdmin):
    list_display=('name','user', 'is_active', 'suspended', 'created_date', 'modified_date', 'expire_date', 'doc_id')
    list_filter  = ['is_active','suspended']
admin.site.register(Actor, ActorAdmin)
