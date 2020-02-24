class PermissionsMixin(object):
    @property
    def permissions(self):
        return [
            perm for permset in self.permission_sets for perm in permset.permissions
        ]
