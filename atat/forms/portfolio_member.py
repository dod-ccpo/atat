from wtforms.validators import Required
from wtforms.fields import BooleanField, FormField

from .forms import BaseForm
from .member import NewForm as BaseNewMemberForm
from atat.domain.permission_sets import PermissionSets
from atat.forms.fields import SelectField
from atat.utils.localization import translate


class PermissionsForm(BaseForm):
    perms_app_mgmt = BooleanField(
        translate("forms.new_member.app_mgmt.label"),
        default=False,
        description=translate("forms.new_member.app_mgmt.description"),
    )
    perms_funding = BooleanField(
        translate("forms.new_member.funding.label"),
        default=False,
        description=translate("forms.new_member.funding.description"),
    )
    perms_reporting = BooleanField(
        translate("forms.new_member.reporting.label"),
        default=False,
        description=translate("forms.new_member.reporting.description"),
    )
    perms_portfolio_mgmt = BooleanField(
        translate("forms.new_member.portfolio_mgmt.label"),
        default=False,
        description=translate("forms.new_member.portfolio_mgmt.description"),
    )

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        perm_sets = []

        if _data["perms_app_mgmt"]:
            perm_sets.append(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)

        if _data["perms_funding"]:
            perm_sets.append(PermissionSets.EDIT_PORTFOLIO_FUNDING)

        if _data["perms_reporting"]:
            perm_sets.append(PermissionSets.EDIT_PORTFOLIO_REPORTS)

        if _data["perms_portfolio_mgmt"]:
            perm_sets.append(PermissionSets.EDIT_PORTFOLIO_ADMIN)

        _data["permission_sets"] = perm_sets
        return _data


class NewForm(PermissionsForm):
    user_data = FormField(BaseNewMemberForm)


class AssignPPOCForm(PermissionsForm):
    role_id = SelectField(
        label=translate("forms.assign_ppoc.dod_id"),
        validators=[Required()],
        choices=[("", "- Select -")],
    )
