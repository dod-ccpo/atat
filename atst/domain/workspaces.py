class Projects(object):
    def __init__(self):
        pass

    def create(self, creator_id, body):
        pass

    def get(self, project_id):
        pass

    def get_many(self, workspace_id):
        return [
            {
                "id": "187c9bea-9541-45d7-801f-cf8e7a642e93",
                "name": "Code.mil",
                "environments": [
                    {
                        "id": "b1154fdd-31c9-437f-b580-2e4d757de5cb",
                        "name": "Development",
                    },
                    {"id": "b1e2077a-6a3d-4e7f-a80c-bf1143433adf", "name": "Sandbox"},
                    {
                        "id": "8ea95eea-7cc0-4500-adf7-8a13eaa6b752",
                        "name": "production",
                    },
                ],
            },
            {
                "id": "ececfd73-b19d-45aa-9199-a950ba2c7269",
                "name": "Digital Dojo",
                "environments": [
                    {
                        "id": "f56167cb-ca3d-4e29-8b60-91052957a118",
                        "name": "Development",
                    },
                    {
                        "id": "7c18689c-5b77-4b68-8d64-d4d8a830bf47",
                        "name": "production",
                    },
                ],
            },
        ]

    def update(self, request_id, request_delta):
        pass


class Members(object):
    def __init__(self):
        pass

    def create(self, creator_id, body):
        pass

    def get(self, request_id):
        pass

    def get_many(self, workspace_id):
        return [
            {
                "first_name": "Danny",
                "last_name": "Knight",
                "email": "dknight@thenavy.mil",
                "dod_id": "1257892124",
                "workspace_role": "Developer",
                "status": "Pending",
                "num_projects": "4",
            },
            {
                "first_name": "Mario",
                "last_name": "Hudson",
                "email": "mhudson@thearmy.mil",
                "dod_id": "4357892125",
                "workspace_role": "CCPO",
                "status": "Active",
                "num_projects": "0",
            },
            {
                "first_name": "Louise",
                "last_name": "Greer",
                "email": "lgreer@theairforce.mil",
                "dod_id": "7257892125",
                "workspace_role": "Admin",
                "status": "Pending",
                "num_projects": "43",
            },
        ]

    def update(self, request_id, request_delta):
        pass
