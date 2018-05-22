from django_serializer.exceptions import ServerError


class PermissionsModelMixin:
    class Permission:
        R = 1       # read permission
        W = 1 << 1  # write permission
        D = 1 << 2  # delete permission

    owner_permission = (Permission.R, Permission.W, Permission.D)
    group_permission = (Permission.R, Permission.W)
    authorized_permission = (Permission.R, )
    unauthorized_permission = ()

    def is_owner(self, user):
        pass

    def in_group(self, user):
        pass


class PermissionsMixin(PermissionsModelMixin):
    class DefaultPermissions(PermissionsModelMixin):
        authorized_permission = (PermissionsModelMixin.Permission.R, PermissionsModelMixin.Permission.W)

    owner_permission = ()
    group_permission = ()
    authorized_permission = ()
    unauthorized_permission = ()

    def get_permissions_object(self):
        conditions = (
            bool(self.owner_permission),
            bool(self.group_permission),
            bool(self.authorized_permission),
            bool(self.unauthorized_permission),
        )

        if any(conditions):
            obj = self
        elif hasattr(self, 'get_object'):
            obj = self.get_object()
        else:
            obj = self.DefaultPermissions()

        return obj

    def get_permissions(self, user):
        if hasattr(self, '_permissions'):
            return getattr(self, '_permissions')

        obj = self.get_permissions_object()

        if user.is_authenticated and obj.is_owner(user):
            permissions = obj.owner_permission
        elif user.is_authenticated and obj.in_group(user):
            permissions = obj.group_permission
        elif user.is_authenticated:
            permissions = obj.authorized_permission
        else:
            permissions = obj.unauthorized_permission

        setattr(self, '_permissions', permissions)

        return permissions

    def check_permission(self, user, permission):
        if user.is_superuser:
            return
        if permission not in self.get_permissions(user):
            raise ServerError(ServerError.ACCESS_DENIED)

    def check_r_permission(self, user):
        self.check_permission(user, PermissionsModelMixin.Permission.R)

    def check_w_permission(self, user):
        self.check_permission(user, PermissionsModelMixin.Permission.W)

    def check_d_permission(self, user):
        self.check_permission(user, PermissionsModelMixin.Permission.D)
