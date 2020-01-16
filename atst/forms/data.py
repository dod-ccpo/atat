from atst.models import CSPRole
from atst.utils.localization import translate


SERVICE_BRANCHES = [
    ("air_force", translate("forms.portfolio.defense_component.choices.air_force")),
    ("army", translate("forms.portfolio.defense_component.choices.army")),
    (
        "marine_corps",
        translate("forms.portfolio.defense_component.choices.marine_corps"),
    ),
    ("navy", translate("forms.portfolio.defense_component.choices.navy")),
    ("other", translate("forms.portfolio.defense_component.choices.other")),
]

ENV_ROLE_NO_ACCESS = "No Access"
ENV_ROLES = [(role.name, role.value) for role in CSPRole] + [
    (ENV_ROLE_NO_ACCESS, ENV_ROLE_NO_ACCESS)
]

JEDI_CLIN_TYPES = [
    ("JEDI_CLIN_1", translate("JEDICLINType.JEDI_CLIN_1")),
    ("JEDI_CLIN_2", translate("JEDICLINType.JEDI_CLIN_2")),
    ("JEDI_CLIN_3", translate("JEDICLINType.JEDI_CLIN_3")),
    ("JEDI_CLIN_4", translate("JEDICLINType.JEDI_CLIN_4")),
]
