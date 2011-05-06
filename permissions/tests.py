# django imports
from django.contrib.flatpages.models import FlatPage
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

# permissions imports
from django.test.testcases import TransactionTestCase
from permissions.models import Permission, Actor, ActorGroup
from permissions.models import ObjectPermission
from permissions.models import ObjectPermissionInheritanceBlock
from permissions.models import Role

import permissions.utils

class BackendTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        settings.AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'permissions.backend.ObjectPermissionsBackend',
        )
        
        self.role_1 = permissions.utils.register_role("Role 1")        
        self.actor = Actor.objects.create(name="john")
        self.page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")
        self.view = permissions.utils.register_permission("View", "view")
        
        # Add actor to role
        self.role_1.add_principal(self.actor)

    def test_has_perm(self):
        """Tests has perm of the backend.
        """
        result = self.actor.has_perm(self.view, self.page_1)
        self.assertEqual(result, False)
        
        # assign view permission to role 1
        permissions.utils.grant_permission(self.page_1, self.role_1, self.view)

        result = self.actor.has_perm("view", self.page_1)
        self.assertEqual(result, True)
    
class RoleTestCase(TestCase):
    """
    """    
    def setUp(self):
        """
        """
        self.role_1 = permissions.utils.register_role("Role 1")
        self.role_2 = permissions.utils.register_role("Role 2")

        self.actor = Actor.objects.create(name="john")
        self.group = ActorGroup.objects.create(name="brights")

        self.actor.groups.add(self.group)

        self.page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")
        self.page_2 = FlatPage.objects.create(url="/page-1/", title="Page 2")
        
    def test_getter(self):
        """
        """
        # Group
        result = permissions.utils.get_group_by_id(self.group.id)
        self.assertEqual(result, self.group)

        result = permissions.utils.get_group(42)
        self.assertEqual(result, None)

        result = permissions.utils.get_group(self.group.name)
        self.assertEqual(result, self.group)

        result = permissions.utils.get_group("Not Existing")
        self.assertEqual(result, None)

        # Role
        result = permissions.utils.get_role_by_id(self.role_1.id)
        self.assertEqual(result, self.role_1)

        result = permissions.utils.get_role(42)
        self.assertEqual(result, None)

        result = permissions.utils.get_role(self.role_1.name)
        self.assertEqual(result, self.role_1)

        result = permissions.utils.get_role("Not Existing")
        self.assertEqual(result, None)

        result = permissions.utils.get_actor_by_id(self.actor.id)
        self.assertEqual(result, self.actor)

        result = permissions.utils.get_actor_by_id(42)
        self.assertEqual(result, None)

        result = permissions.utils.get_actor(self.actor.name)
        self.assertEqual(result, self.actor)

        result = permissions.utils.get_actor("Not Existing")
        self.assertEqual(result, None)

    def test_global_roles_actor(self):
        """
        """
        # Add role 1
        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        # Add role 1 again
        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [self.role_1])

        # Add role 2
        result = permissions.utils.add_role(self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [self.role_1, self.role_2])

        # Remove role 1
        result = permissions.utils.remove_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = permissions.utils.remove_role(self.actor, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [self.role_2])

        # Remove role 2
        result = permissions.utils.remove_role(self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [])

    def test_global_roles_group(self):
        """
        """
        # Add role 1
        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Add role 1 again
        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1])

        # Add role 2
        result = permissions.utils.add_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = permissions.utils.remove_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = permissions.utils.remove_role(self.group, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = permissions.utils.remove_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [])

    def test_remove_roles_actor(self):
        """
        """
        # Add role 1
        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        # Add role 2
        result = permissions.utils.add_role(self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [self.role_1, self.role_2])

        # Remove roles
        result = permissions.utils.remove_roles(self.actor)
        self.assertEqual(result, True)

        result = permissions.utils.get_roles(self.actor)
        self.assertEqual(list(result), [])

        # Remove roles
        result = permissions.utils.remove_roles(self.actor)
        self.assertEqual(result, False)

    def test_remove_roles_group(self):
        """
        """
        # Add role 1
        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Add role 2
        result = permissions.utils.add_role(self.group, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove roles
        result = permissions.utils.remove_roles(self.group)
        self.assertEqual(result, True)

        result = permissions.utils.get_global_roles(self.group)
        self.assertEqual(result, [])

        # Remove roles
        result = permissions.utils.remove_roles(self.group)
        self.assertEqual(result, False)

    def test_local_role_actor(self):
        """
        """
        # Add local role to page 1
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, True)

        # Again
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [self.role_1])

        # Add local role 2
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = permissions.utils.remove_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = permissions.utils.remove_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = permissions.utils.remove_local_role(self.page_1, self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [])

    def test_local_role_group(self):
        """
        """
        # Add local role to page 1
        result = permissions.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        # Again
        result = permissions.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_1])

        # Add local role 2
        result = permissions.utils.add_local_role(self.page_1, self.group, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove role 1
        result = permissions.utils.remove_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        # Remove role 1 again
        result = permissions.utils.remove_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, False)

        result = permissions.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [self.role_2])

        # Remove role 2
        result = permissions.utils.remove_local_role(self.page_1, self.group, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.group)
        self.assertEqual(result, [])

    def test_remove_local_roles_actor(self):
        """
        """
        # Add local role to page 1
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, True)

        # Add local role 2
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_2)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [self.role_1, self.role_2])

        # Remove all local roles
        result = permissions.utils.remove_local_roles(self.page_1, self.actor)
        self.assertEqual(result, True)

        result = permissions.utils.get_local_roles(self.page_1, self.actor)
        self.assertEqual(result, [])

        # Remove all local roles again
        result = permissions.utils.remove_local_roles(self.page_1, self.actor)
        self.assertEqual(result, False)

    def test_get_groups_1(self):
        """Tests global roles for groups.
        """
        result = self.role_1.get_groups()
        self.assertEqual(len(result), 0)

        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        result = self.role_1.get_groups()
        self.assertEqual(result[0].name, "brights")

        # Add another group
        self.group_2 = ActorGroup.objects.create(name="atheists")
        result = permissions.utils.add_role(self.group_2, self.role_1)

        result = self.role_1.get_groups()
        self.assertEqual(result[0].name, "brights")
        self.assertEqual(result[1].name, "atheists")
        self.assertEqual(len(result), 2)

        # Add the role to an actor
        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        # This shouldn't have an effect on the result
        result = self.role_1.get_groups()
        self.assertEqual(result[0].name, "brights")
        self.assertEqual(result[1].name, "atheists")
        self.assertEqual(len(result), 2)

    def test_get_groups_2(self):
        """Tests local roles for groups.
        """
        result = self.role_1.get_groups(self.page_1)
        self.assertEqual(len(result), 0)

        result = permissions.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        result = self.role_1.get_groups(self.page_1)
        self.assertEqual(result[0].name, "brights")

        # Add another local group
        self.group_2 = ActorGroup.objects.create(name="atheists")
        result = permissions.utils.add_local_role(self.page_1, self.group_2, self.role_1)

        result = self.role_1.get_groups(self.page_1)
        self.assertEqual(result[0].name, "brights")
        self.assertEqual(result[1].name, "atheists")

        # A the global role to group
        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # Nontheless there are just two groups returned (and no duplicate)
        result = self.role_1.get_groups(self.page_1)
        self.assertEqual(result[0].name, "brights")
        self.assertEqual(result[1].name, "atheists")
        self.assertEqual(len(result), 2)

        # Andere there should one global role
        result = self.role_1.get_groups()
        self.assertEqual(result[0].name, "brights")

        # Add the role to an actor
        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, True)

        # This shouldn't have an effect on the result
        result = self.role_1.get_groups(self.page_1)
        self.assertEqual(result[0].name, "brights")
        self.assertEqual(result[1].name, "atheists")
        self.assertEqual(len(result), 2)

    def test_get_actors_1(self):
        """Tests global roles for actors.
        """
        result = self.role_1.get_actors()
        self.assertEqual(len(result), 0)

        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        result = self.role_1.get_actors()
        self.assertEqual(result[0].name, "john")

        # Add another role to an actor
        self.actor_2 = Actor.objects.create(name="jane")
        result = permissions.utils.add_role(self.actor_2, self.role_1)

        result = self.role_1.get_actors()
        self.assertEqual(result[0].name, "john")
        self.assertEqual(result[1].name, "jane")
        self.assertEqual(len(result), 2)

        # Add the role to an actor
        result = permissions.utils.add_role(self.group, self.role_1)
        self.assertEqual(result, True)

        # This shouldn't have an effect on the result
        result = self.role_1.get_actors()
        self.assertEqual(result[0].name, "john")
        self.assertEqual(result[1].name, "jane")
        self.assertEqual(len(result), 2)

    def test_get_actors_2(self):
        """Tests local roles for actors.
        """
        result = self.role_1.get_actors(self.page_1)
        self.assertEqual(len(result), 0)

        result = permissions.utils.add_local_role(self.page_1, self.actor, self.role_1)
        self.assertEqual(result, True)

        result = self.role_1.get_actors(self.page_1)
        self.assertEqual(result[0].name, "john")

        # Add another local role to an actor
        self.actor_2 = Actor.objects.create(name="jane")
        result = permissions.utils.add_local_role(self.page_1, self.actor_2, self.role_1)

        result = self.role_1.get_actors(self.page_1)
        self.assertEqual(result[0].name, "john")
        self.assertEqual(result[1].name, "jane")

        # A the global role to actor
        result = permissions.utils.add_role(self.actor, self.role_1)
        self.assertEqual(result, True)

        # Nontheless there are just two actors returned (and no duplicate)
        result = self.role_1.get_actors(self.page_1)
        self.assertEqual(result[0].name, "john")
        self.assertEqual(result[1].name, "jane")
        self.assertEqual(len(result), 2)

        # Andere there should one actor for the global role
        result = self.role_1.get_actors()
        self.assertEqual(result[0].name, "john")

        # Add the role to an group
        result = permissions.utils.add_local_role(self.page_1, self.group, self.role_1)
        self.assertEqual(result, True)

        # This shouldn't have an effect on the result
        result = self.role_1.get_actors(self.page_1)
        self.assertEqual(result[0].name, "john")
        self.assertEqual(result[1].name, "jane")
        self.assertEqual(len(result), 2)
        
    def test_get_actors_3(self):
        """
        """
        self.role_1.add_principal(self.actor)
        result = self.role_1.get_actors()
        self.assertEqual(result, [self.actor])
        
        # Add same actor again
        self.role_1.add_principal(self.actor)
        result = self.role_1.get_actors()
        self.assertEqual(result, [self.actor])

class PermissionTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.role_1 = permissions.utils.register_role("Role 1")
        self.role_2 = permissions.utils.register_role("Role 2")

        self.actor = Actor.objects.create(name="john")
        permissions.utils.add_role(self.actor, self.role_1)
        self.actor.save()

        self.page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")
        self.page_2 = FlatPage.objects.create(url="/page-1/", title="Page 2")

        self.permission = permissions.utils.register_permission("View", "view")

    def test_add_permissions(self):
        """
        """
        # Add per object
        result = permissions.utils.grant_permission(self.page_1, self.role_1, self.permission)
        self.assertEqual(result, True)

        # Add per codename
        result = permissions.utils.grant_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, True)

        # Add ermission which does not exist
        result = permissions.utils.grant_permission(self.page_1, self.role_1, "hurz")
        self.assertEqual(result, False)

    def test_remove_permission(self):
        """
        """
        # Add
        result = permissions.utils.grant_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, True)

        # Remove
        result = permissions.utils.remove_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, True)

        # Remove again
        result = permissions.utils.remove_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, False)

    def test_has_permission_role(self):
        """
        """
        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, False)

        result = permissions.utils.grant_permission(self.page_1, self.role_1, self.permission)
        self.assertEqual(result, True)

        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, True)

        result = permissions.utils.remove_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, True)

        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, False)

    def test_has_permission_owner(self):
        """
        """
        creator = Actor.objects.create(name="jane")

        result = permissions.utils.has_permission(self.page_1, creator, "view")
        self.assertEqual(result, False)

        owner = permissions.utils.register_role("Owner")
        permissions.utils.grant_permission(self.page_1, owner, "view")

        result = permissions.utils.has_permission(self.page_1, creator, "view", [owner])
        self.assertEqual(result, True)

    def test_local_role(self):
        """
        """
        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, False)

        permissions.utils.grant_permission(self.page_1, self.role_2, self.permission)
        permissions.utils.add_local_role(self.page_1, self.actor, self.role_2)

        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, True)

    def test_ineritance(self):
        """
        """
        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, True)

        # per permission
        permissions.utils.add_inheritance_block(self.page_1, self.permission)

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, False)

        permissions.utils.remove_inheritance_block(self.page_1, self.permission)

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, True)

        # per codename
        permissions.utils.add_inheritance_block(self.page_1, "view")

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, False)

        permissions.utils.remove_inheritance_block(self.page_1, "view")

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, True)

    def test_unicode(self):
        """
        """
        # Permission
        self.assertEqual(self.permission.__unicode__(), u"View (view)")

        # ObjectPermission
        permissions.utils.grant_permission(self.page_1, self.role_1, self.permission)
        opr = ObjectPermission.objects.get(permission=self.permission, role=self.role_1)
        self.assertEqual(opr.__unicode__(), u"View / %s / flat page - %s" % (self.role_1, self.page_1.id))

        # ObjectPermissionInheritanceBlock
        permissions.utils.add_inheritance_block(self.page_1, self.permission)
        opb = ObjectPermissionInheritanceBlock.objects.get(permission=self.permission)

        self.assertEqual(opb.__unicode__(), u"View (view) / flat page - %s" % (self.page_1.id))

    def test_reset(self):
        """
        """
        result = permissions.utils.grant_permission(self.page_1, self.role_1, "view")
        self.assertEqual(result, True)

        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, True)

        permissions.utils.add_inheritance_block(self.page_1, "view")

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, False)

        permissions.utils.reset(self.page_1)

        result = permissions.utils.has_permission(self.page_1, self.actor, "view")
        self.assertEqual(result, False)

        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, True)

        permissions.utils.reset(self.page_1)

class RegistrationTestCase(TransactionTestCase):
    """Tests the registration of different components.
    """
    def test_group(self):
        """Tests registering/unregistering of a group.
        """
        # Register a group
        result = permissions.utils.register_group("Brights")
        self.failUnless(isinstance(result, ActorGroup))

        # It's there
        group = ActorGroup.objects.get(name="Brights")
        self.assertEqual(group.name, "Brights")

        # Trying to register another group with same name
        result = permissions.utils.register_group("Brights")
        self.assertEqual(result, False)

        group = ActorGroup.objects.get(name="Brights")
        self.assertEqual(group.name, "Brights")

        # Unregister the group
        result = permissions.utils.unregister_group("Brights")
        self.assertEqual(result, True)

        # It's not there anymore
        self.assertRaises(ActorGroup.DoesNotExist, ActorGroup.objects.get, name="Brights")

        # Trying to unregister the group again
        result = permissions.utils.unregister_group("Brights")
        self.assertEqual(result, False)

    def test_role(self):
        """Tests registering/unregistering of a role.
        """
        # Register a role
        result = permissions.utils.register_role("Editor")
        self.failUnless(isinstance(result, Role))

        # It's there
        role = Role.objects.get(name="Editor")
        self.assertEqual(role.name, "Editor")

        # Trying to register another role with same name
        result = permissions.utils.register_role("Editor")
        self.assertEqual(result, False)

        role = Role.objects.get(name="Editor")
        self.assertEqual(role.name, "Editor")

        # Unregister the role
        result = permissions.utils.unregister_role("Editor")
        self.assertEqual(result, True)

        # It's not there anymore
        self.assertRaises(Role.DoesNotExist, Role.objects.get, name="Editor")

        # Trying to unregister the role again
        result = permissions.utils.unregister_role("Editor")
        self.assertEqual(result, False)

    def test_permission(self):
        """Tests registering/unregistering of a permission.
        """
        # Register a permission
        result = permissions.utils.register_permission("Change", "change")
        self.failUnless(isinstance(result, Permission))

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Register a permission with the same codename
        result = permissions.utils.register_permission("Change2", "change")
        self.assertEqual(result, False)

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Register a permission with the same name
        result = permissions.utils.register_permission("Change", "change2")
        self.assertEqual(result, False)

        # Is it there?
        p = Permission.objects.get(codename="change")
        self.assertEqual(p.name, "Change")

        # Unregister the permission
        result = permissions.utils.unregister_permission("change")
        self.assertEqual(result, True)

        # Is it not there anymore?
        self.assertRaises(Permission.DoesNotExist, Permission.objects.get, codename="change")

        # Unregister the permission again
        result = permissions.utils.unregister_permission("change")
        self.assertEqual(result, False)

# django imports
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.sessions.backends.file import SessionStore
from django.test.client import Client

# Taken from "http://www.djangosnippets.org/snippets/963/"
class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

def create_request():
    """
    """
    rf = RequestFactory()
    request = rf.get('/')
    request.session = SessionStore()

    actor = Actor()
    #actor.is_supeactor = True
    actor.save()
    request.actor = actor

    return request