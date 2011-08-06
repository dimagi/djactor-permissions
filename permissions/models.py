# django imports
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
import logging
import uuid
def make_uuid():
    return uuid.uuid4().hex

class ActorGroup(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    name = models.CharField(_("Actor Group Name"), max_length=160, unique=True)


    class Meta:
        ordering = ("name", )

def _actor_has_perm(actor, perm, obj):
    logging.error("actor_has_perm #%s# #%s# #%s#" % (actor, perm, obj))
    for backend in auth.get_backends():
        logging.error("using backend %s" % (backend))
        if hasattr(backend, "has_perm"):
            logging.error("using has_perm")
            if obj is not None:
                if (backend.supports_object_permissions and
                    backend.has_perm(actor, perm, obj)):
                        return True
            else:
                if backend.has_perm(actor, perm):
                    return True
    return False


def _actor_has_module_perms(actor, app_label):
    for backend in auth.get_backends():
        if hasattr(backend, "has_module_perms"):
            if backend.has_module_perms(actor, app_label):
                return True
    return False


class Actor(models.Model):
    """
    Actors are one level of abstraction provided for uniquely identifying a role or set of roles for a given user.
    A user can have multiple actors for it, each having a unique set of roles given to it.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    doc_id = models.CharField(max_length=32, unique=True, null=True, db_index=True)

    name = models.CharField(_("Actor Name"), max_length=160, unique=True)
    user = models.ForeignKey(User, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    suspended = models.BooleanField(default=False)

    created_date = models.DateTimeField(default=datetime.utcnow)
    modified_date = models.DateTimeField(default=datetime.utcnow)
    expire_date = models.DateTimeField(null=True, blank=True)

    groups = models.ManyToManyField(ActorGroup, blank=True, null=True)

    class Meta:
        ordering = ('created_date',)

    def __unicode__(self):
        return "Actor (%s) %s" % (self.id, self.name)


    #taken from the User model for permission handling
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object
        is provided, permissions for this specific object are checked.
        """
        # Inactive users have no permissions.
        if not self.is_active:
            return False
        # Superusers have all permissions.
        if self.suspended:
            return False

        # Otherwise we need to check the backends.
        return _actor_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions.
        If object is passed, it checks if the user has all required perms
        for this object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app
        label. Uses pretty much the same logic as has_perm, above.
        """
        if not self.is_active:
            return False

        if self.is_suspended:
            return False

        return _actor_has_module_perms(self, app_label)




# permissions imports
import permissions.utils

class Permission(models.Model):
    """A permission which can be granted to users/groups and objects.

    **Attributes:**

    name
        The unique name of the permission. This is displayed to users.

    codename
        The unique codename of the permission. This is used internal to
        identify a permission.

    content_types
        The content types for which the permission is active. This can be
        used to display only reasonable permissions for an object.
    """
    name = models.CharField(_(u"Name"), max_length=100, unique=True)
    codename = models.CharField(_(u"Codename"), max_length=100, unique=True)
    content_types = models.ManyToManyField(ContentType, verbose_name=_(u"Content Types"), blank=True, null=True, related_name="content_types")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.codename)

class ObjectPermission(models.Model):
    """Grants permission for a role and an content object (optional).

    **Attributes:**

    role
        The role for which the permission is granted.

    permission
        The permission which is granted.

    content
        The object for which the permission is granted.
    """
    role = models.ForeignKey("Role", verbose_name=_(u"Role"), blank=True, null=True)
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"))
    content_id = models.CharField(max_length=32, verbose_name=_(u"Content id"))
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    def __unicode__(self):
        return "%s / %s / %s - %s" % (self.permission.name, self.role, self.content_type, self.content_id)

class ObjectPermissionInheritanceBlock(models.Model):
    """Blocks the inheritance for specific permission and object.

    **Attributes:**

    permission
        The permission for which inheritance is blocked.

    content
        The object for which the inheritance is blocked.
    """
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"))
    content_id = models.PositiveIntegerField(verbose_name=_(u"Content id"))
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    def __unicode__(self):
        return "%s / %s - %s" % (self.permission, self.content_type, self.content_id)

class Role(models.Model):
    """A role gets permissions to do something. Principals (users and groups)
    can only get permissions via roles.

    **Attributes:**

    name
        The unique name of the role
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name", ]

    def __unicode__(self):
        return self.name

    def add_principal(self, principal, content=None):
        """Addes the given principal (user or group) ot the Role.
        """
        return permissions.utils.add_role(principal, self)

    def get_groups(self, content=None):
        """Returns all groups which has this role assigned. If content is given
        it returns also the local roles.
        """
        if content:
            ctype = ContentType.objects.get_for_model(content)
            prrs = PrincipalRoleRelation.objects.filter(role=self,
                content_id__in = (None, content.id),
                content_type__in = (None, ctype)).exclude(group=None)
        else:
            prrs = PrincipalRoleRelation.objects.filter(role=self,
            content_id=None, content_type=None).exclude(group=None)

        return [prr.group for prr in prrs]

    def get_actors(self, content=None):
        """Returns all users which has this role assigned. If content is given
        it returns also the local roles.
        """
        if content:
            ctype = ContentType.objects.get_for_model(content)
            prrs = PrincipalRoleRelation.objects.filter(role=self,
                content_id__in = (None, content.id),
                content_type__in = (None, ctype)).exclude(actor=None)
        else:
            prrs = PrincipalRoleRelation.objects.filter(role=self,
                content_id=None, content_type=None).exclude(actor=None)

        return [prr.actor for prr in prrs]

class PrincipalRoleRelation(models.Model):
    """A role given to a principal (user or group). If a content object is
    given this is a local role, i.e. the principal has this role only for this
    content object. Otherwise it is a global role, i.e. the principal has
    this role generally.

    user
        A user instance. Either a user xor a group needs to be given.

    group
        A group instance. Either a user xor a group needs to be given.

    role
        The role which is given to the principal for content.

    content
        The content object which gets the local role (optional).
    """
    actor = models.ForeignKey(Actor, verbose_name=_(u"Actor"), blank=True, null=True)
    group = models.ForeignKey(ActorGroup, verbose_name=_(u"ActorGroup"), blank=True, null=True)
    role = models.ForeignKey(Role, verbose_name=_(u"Role"))

    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), blank=True, null=True)
    content_id = models.CharField(max_length=32, verbose_name=_(u"Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")

    class Meta:
        order_with_respect_to='role'
    
    def __unicode__(self):
        if self.actor:
            principal = self.actor.name
        else:
            principal = self.group
        
        return "%s - %s" % (principal, self.role)
        
    def get_principal(self):
        """Returns the principal.
        """
        return self.actor or self.group

    def set_principal(self, principal):
        """Sets the principal.
        """
        if isinstance(principal, Actor):
            self.actor = principal
        else:
            self.group = principal

    principal = property(get_principal, set_principal)
