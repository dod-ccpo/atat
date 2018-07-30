class Permissions(object):
    REQUEST_JEDI_WORKSPACE = "request_jedi_workspace"
    VIEW_ORIGINAL_JEDI_REQEUST = "view_original_jedi_request"
    REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST = (
        "review_and_approve_jedi_workspace_request"
    )
    MODIFY_ATAT_ROLE_PERMISSIONS = "modify_atat_role_permissions"
    CREATE_CSP_ROLE = "create_csp_role"
    DELETE_CSP_ROLE = "delete_csp_role"
    DEACTIVE_CSP_ROLE = "deactivate_csp_role"
    MODIFY_CSP_ROLE_PERMISSIONS = "modify_csp_role_permissions"

    VIEW_USAGE_REPORT = "view_usage_report"
    VIEW_USAGE_DOLLARS = "view_usage_dollars"
    ADD_AND_ASSIGN_CSP_ROLES = "add_and_assign_csp_roles"
    REMOVE_CSP_ROLES = "remove_csp_roles"
    REQUEST_NEW_CSP_ROLE = "request_new_csp_role"
    ASSIGN_AND_UNASSIGN_ATAT_ROLE = "assign_and_unassign_atat_role"

    VIEW_ASSIGNED_ATAT_ROLE_CONFIGURATIONS = "view_assigned_atat_role_configurations"
    VIEW_ASSIGNED_CSP_ROLE_CONFIGURATIONS = "view_assigned_csp_role_configurations"

    DEACTIVATE_WORKSPACE = "deactivate_workspace"
    VIEW_ATAT_PERMISSIONS = "view_atat_permissions"
    TRANSFER_OWNERSHIP_OF_WORKSPACE = "transfer_ownership_of_workspace"

    ADD_APPLICATION_IN_WORKSPACE = "add_application_in_workspace"
    DELETE_APPLICATION_IN_WORKSPACE = "delete_application_in_workspace"
    DEACTIVATE_APPLICATION_IN_WORKSPACE = "deactivate_application_in_workspace"
    VIEW_APPLICATION_IN_WORKSPACE = "view_application_in_workspace"
    RENAME_APPLICATION_IN_WORKSPACE = "rename_application_in_workspace"

    ADD_ENVIRONMENT_IN_APPLICATION = "add_environment_in_application"
    DELETE_ENVIRONMENT_IN_APPLICATION = "delete_environment_in_application"
    DEACTIVATE_ENVIRONMENT_IN_APPLICATION = "deactivate_environment_in_application"
    VIEW_ENVIRONMENT_IN_APPLICATION = "view_environment_in_application"
    RENAME_ENVIRONMENT_IN_APPLICATION = "rename_environment_in_application"

    ADD_TAG_TO_WORKSPACE = "add_tag_to_workspace"
    REMOVE_TAG_FROM_WORKSPACE = "remove_tag_from_workspace"
