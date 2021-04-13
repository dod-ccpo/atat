data-feeder
    - add
        - atat-user
            --dod-id
            --name
            --last
            --email
            --phone
            --ext
            --branch
            --citizenship
            --designation
            --feed-json
            --file-json
        - portaforlio
            --owner-dod-id
            --name
            --desc
            --branch
            --feed-json
            --file-json
        - task-order
            --to-file
            --to-number
            --add-clin
                --clin
                --idiq-clin
                --total-value
                --obligate-funds
                --pop-start-date
                --pop-end-date
            --confirm-to
            --confirm-true
        - user-portfolio-set
            --user-dod-id
            --user-id
            --portafolio-id
            --permision-set-name
            --permision-set-id
    - get
        - atat-user
            --by-dod-id
            --by-atat-id
            --format
        - atat-users
            --format
        - portaforlio
            --by-id
            --format
            --format-branches
        - portaforlios
            --format
        - task-order
            --by-id
            --format
            --format-clin-types
        -task-orders
            --by-portfolio
            --all
            --format
        - user-portfolio-set
            --by-portfolio
            --by-user
            --all
            --format
    --help




to create a user:
/dev-new-user?first_name=Harrold&last_name=Henderson&dod_id=1234567890
d


portfolio owner is name PRIMARY POINT OF CONTACT

Relations:
            portfolio roles permission set >-- permission set
                            |
                            ^
user --< portfolio roles (portfolio + user + role) >-- portfolio


https://localhost:8000/portfolios/new
- user_id

```

SELECT users.time_created AS users_time_created, users.time_updated AS users_time_updated, users.id AS users_id, users.username AS users_username, users.email AS users_email, users.dod_id AS users_dod_id, users.first_name AS users_first_name, users.last_name AS users_last_name, users.phone_number AS users_phone_number, users.phone_ext AS users_phone_ext, users.service_branch AS users_service_branch, users.citizenship AS users_citizenship, users.designation AS users_designation, users.last_login AS users_last_login, users.last_session_id AS users_last_session_id, users.cloud_id AS users_cloud_id 
FROM users 
WHERE users.id = %(id_1)s


SELECT permission_sets.time_created AS permission_sets_time_created, permission_sets.time_updated AS permission_sets_time_updated, permission_sets.id AS permission_sets_id, permission_sets.name AS permission_sets_name, permission_sets.display_name AS permission_sets_display_name, permission_sets.description AS permission_sets_description, permission_sets.permissions AS permission_sets_permissions 
FROM permission_sets 
WHERE permission_sets.name IN (%(name_1)s, %(name_2)s, %(name_3)s, %(name_4)s, %(name_5)s, %(name_6)s, %(name_7)s, %(name_8)s, %(name_9)s, %(name_10)s)


INSERT INTO portfolios (name, defense_component, app_migration, complexity, complexity_other, description, dev_team, dev_team_other, native_apps, team_experience) VALUES (%(name)s, %(defense_component)s, %(app_migration)s, %(complexity)s, %(complexity_other)s, %(description)s, %(dev_team)s, %(dev_team_other)s, %(native_apps)s, %(team_experience)s) RETURNING portfolios.id


INSERT INTO portfolio_roles (portfolio_id, user_id, status) VALUES (%(portfolio_id)s, %(user_id)s, %(status)s) RETURNING portfolio_roles.id

	
INSERT INTO portfolio_roles_permission_sets (portfolio_role_id, permission_set_id) VALUES (%(portfolio_role_id)s, %(permission_set_id)s)


SELECT portfolios.time_created AS portfolios_time_created, portfolios.time_updated AS portfolios_time_updated, portfolios.deleted AS portfolios_deleted, portfolios.id AS portfolios_id, portfolios.name AS portfolios_name, portfolios.defense_component AS portfolios_defense_component, portfolios.app_migration AS portfolios_app_migration, portfolios.complexity AS portfolios_complexity, portfolios.complexity_other AS portfolios_complexity_other, portfolios.description AS portfolios_description, portfolios.dev_team AS portfolios_dev_team, portfolios.dev_team_other AS portfolios_dev_team_other, portfolios.native_apps AS portfolios_native_apps, portfolios.team_experience AS portfolios_team_experience, portfolios.csp_data AS portfolios_csp_data 
FROM portfolios 
WHERE portfolios.id = %(param_1)s
```
