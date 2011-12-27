# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ActorGroup'
        db.create_table('permissions_actorgroup', (
            ('id', self.gf('django.db.models.fields.CharField')(default='ece0f19ae22947a490917d3690a68ddd', unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=160)),
        ))
        db.send_create_signal('permissions', ['ActorGroup'])

        # Adding model 'Actor'
        db.create_table('permissions_actor', (
            ('id', self.gf('django.db.models.fields.CharField')(default='3e0ba771c7dd40839f2ce130107cd12f', unique=True, max_length=32, primary_key=True)),
            ('doc_id', self.gf('django.db.models.fields.CharField')(max_length=32, unique=True, null=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=160)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='actors', null=True, to=orm['auth.User'])),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('suspended', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('expire_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('permissions', ['Actor'])

        # Adding M2M table for field groups on 'Actor'
        db.create_table('permissions_actor_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('actor', models.ForeignKey(orm['permissions.actor'], null=False)),
            ('actorgroup', models.ForeignKey(orm['permissions.actorgroup'], null=False))
        ))
        db.create_unique('permissions_actor_groups', ['actor_id', 'actorgroup_id'])

        # Adding model 'Permission'
        db.create_table('permissions_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('permissions', ['Permission'])

        # Adding M2M table for field content_types on 'Permission'
        db.create_table('permissions_permission_content_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(orm['permissions.permission'], null=False)),
            ('contenttype', models.ForeignKey(orm['contenttypes.contenttype'], null=False))
        ))
        db.create_unique('permissions_permission_content_types', ['permission_id', 'contenttype_id'])

        # Adding model 'ObjectPermission'
        db.create_table('permissions_objectpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Role'], null=True, blank=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Permission'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('permissions', ['ObjectPermission'])

        # Adding model 'ObjectPermissionInheritanceBlock'
        db.create_table('permissions_objectpermissioninheritanceblock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Permission'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('permissions', ['ObjectPermissionInheritanceBlock'])

        # Adding model 'Role'
        db.create_table('permissions_role', (
            ('id', self.gf('django.db.models.fields.CharField')(default='5c3156cf929f4596a13a31f778f88915', unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=160)),
        ))
        db.send_create_signal('permissions', ['Role'])

        # Adding model 'PrincipalRoleRelation'
        db.create_table('permissions_principalrolerelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('actor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='principal_roles', null=True, to=orm['permissions.Actor'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.ActorGroup'], null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['permissions.Role'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('content_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('permissions', ['PrincipalRoleRelation'])


    def backwards(self, orm):
        
        # Deleting model 'ActorGroup'
        db.delete_table('permissions_actorgroup')

        # Deleting model 'Actor'
        db.delete_table('permissions_actor')

        # Removing M2M table for field groups on 'Actor'
        db.delete_table('permissions_actor_groups')

        # Deleting model 'Permission'
        db.delete_table('permissions_permission')

        # Removing M2M table for field content_types on 'Permission'
        db.delete_table('permissions_permission_content_types')

        # Deleting model 'ObjectPermission'
        db.delete_table('permissions_objectpermission')

        # Deleting model 'ObjectPermissionInheritanceBlock'
        db.delete_table('permissions_objectpermissioninheritanceblock')

        # Deleting model 'Role'
        db.delete_table('permissions_role')

        # Deleting model 'PrincipalRoleRelation'
        db.delete_table('permissions_principalrolerelation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'permissions.actor': {
            'Meta': {'ordering': "('created_date',)", 'object_name': 'Actor'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'doc_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'expire_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['permissions.ActorGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'46ee8b9596d644d8961ac511874317c8'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'actors'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'permissions.actorgroup': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ActorGroup'},
            'id': ('django.db.models.fields.CharField', [], {'default': "'1020f150073a423c9d0ba93234a3b352'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '160'})
        },
        'permissions.objectpermission': {
            'Meta': {'object_name': 'ObjectPermission'},
            'content_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Role']", 'null': 'True', 'blank': 'True'})
        },
        'permissions.objectpermissioninheritanceblock': {
            'Meta': {'object_name': 'ObjectPermissionInheritanceBlock'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Permission']"})
        },
        'permissions.permission': {
            'Meta': {'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'content_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'permissions.principalrolerelation': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'PrincipalRoleRelation'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'principal_roles'", 'null': 'True', 'to': "orm['permissions.Actor']"}),
            'content_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.ActorGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['permissions.Role']"})
        },
        'permissions.role': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Role'},
            'display': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'id': ('django.db.models.fields.CharField', [], {'default': "'f8f041400ca8405e8505c093550a8ca6'", 'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['permissions']
