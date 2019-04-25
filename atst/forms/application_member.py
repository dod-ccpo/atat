from flask_wtf import FlaskForm
from wtforms.fields import FormField, FieldList, HiddenField, BooleanField

from .forms import BaseForm
from .member import NewForm as BaseNewMemberForm
from .data import FORMATTED_ENV_ROLES as ENV_ROLES
from atst.forms.fields import SelectField
from atst.domain.permission_sets import PermissionSets
from atst.utils.localization import translate


class EnvironmentForm(FlaskForm):
    environment_id = HiddenField()
    environment_name = HiddenField()
    role = SelectField(
        environment_name,
        choices=ENV_ROLES,
        default=None,
        filters=[lambda x: None if x == "None" else x],
    )


class PermissionsForm(FlaskForm):
    perms_env_mgmt = BooleanField(
        translate("portfolios.applications.members.new.manage_envs"), default=False
    )
    perms_team_mgmt = BooleanField(
        translate("portfolios.applications.members.new.manage_team"), default=False
    )
    perms_del_env = BooleanField(
        translate("portfolios.applications.members.new.delete_envs"), default=False
    )

    @property
    def data(self):
        _data = super().data
        perm_sets = []

        if _data["perms_env_mgmt"]:
            perm_sets.append(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)

        if _data["perms_team_mgmt"]:
            perm_sets.append(PermissionSets.EDIT_APPLICATION_TEAM)

        if _data["perms_del_env"]:
            perm_sets.append(PermissionSets.DELETE_APPLICATION_ENVIRONMENTS)

        return perm_sets


class NewForm(BaseForm):
    user_data = FormField(BaseNewMemberForm)
    permission_sets = FormField(PermissionsForm)
    environment_roles = FieldList(FormField(EnvironmentForm))
