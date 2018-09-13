SERVICE_BRANCHES = [
    (None, "Select an option"),
    ("Air Force, Department of the", "Air Force, Department of the"),
    ("Army and Air Force Exchange Service", "Army and Air Force Exchange Service"),
    ("Army, Department of the", "Army, Department of the"),
    (
        "Defense Advanced Research Projects Agency",
        "Defense Advanced Research Projects Agency",
    ),
    ("Defense Commissary Agency", "Defense Commissary Agency"),
    ("Defense Contract Audit Agency", "Defense Contract Audit Agency"),
    ("Defense Contract Management Agency", "Defense Contract Management Agency"),
    ("Defense Finance & Accounting Service", "Defense Finance & Accounting Service"),
    ("Defense Health Agency", "Defense Health Agency"),
    ("Defense Information System Agency", "Defense Information System Agency"),
    ("Defense Intelligence Agency", "Defense Intelligence Agency"),
    ("Defense Legal Services Agency", "Defense Legal Services Agency"),
    ("Defense Logistics Agency", "Defense Logistics Agency"),
    ("Defense Media Activity", "Defense Media Activity"),
    ("Defense Micro Electronics Activity", "Defense Micro Electronics Activity"),
    ("Defense POW-MIA Accounting Agency", "Defense POW-MIA Accounting Agency"),
    ("Defense Security Cooperation Agency", "Defense Security Cooperation Agency"),
    ("Defense Security Service", "Defense Security Service"),
    ("Defense Technical Information Center", "Defense Technical Information Center"),
    (
        "Defense Technology Security Administration",
        "Defense Technology Security Administration",
    ),
    ("Defense Threat Reduction Agency", "Defense Threat Reduction Agency"),
    ("DoD Education Activity", "DoD Education Activity"),
    ("DoD Human Recourses Activity", "DoD Human Recourses Activity"),
    ("DoD Inspector General", "DoD Inspector General"),
    ("DoD Test Resource Management Center", "DoD Test Resource Management Center"),
    (
        "Headquarters Defense Human Resource Activity ",
        "Headquarters Defense Human Resource Activity ",
    ),
    ("Joint Staff", "Joint Staff"),
    ("Missile Defense Agency", "Missile Defense Agency"),
    ("National Defense University", "National Defense University"),
    (
        "National Geospatial Intelligence Agency (NGA)",
        "National Geospatial Intelligence Agency (NGA)",
    ),
    (
        "National Oceanic and Atmospheric Administration (NOAA)",
        "National Oceanic and Atmospheric Administration (NOAA)",
    ),
    ("National Reconnaissance Office", "National Reconnaissance Office"),
    ("National Reconnaissance Office (NRO)", "National Reconnaissance Office (NRO)"),
    ("National Security Agency (NSA)", "National Security Agency (NSA)"),
    (
        "National Security Agency-Central Security Service",
        "National Security Agency-Central Security Service",
    ),
    ("Navy, Department of the", "Navy, Department of the"),
    ("Office of Economic Adjustment", "Office of Economic Adjustment"),
    ("Office of the Secretary of Defense", "Office of the Secretary of Defense"),
    ("Pentagon Force Protection Agency", "Pentagon Force Protection Agency"),
    (
        "Uniform Services University of the Health Sciences",
        "Uniform Services University of the Health Sciences",
    ),
    ("US Cyber Command (USCYBERCOM)", "US Cyber Command (USCYBERCOM)"),
    (
        "US Special Operations Command (USSOCOM)",
        "US Special Operations Command (USSOCOM)",
    ),
    ("US Strategic Command (USSTRATCOM)", "US Strategic Command (USSTRATCOM)"),
    (
        "US Transportation Command (USTRANSCOM)",
        "US Transportation Command (USTRANSCOM)",
    ),
    ("Washington Headquarters Services", "Washington Headquarters Services"),
]

ASSISTANCE_ORG_TYPES = [
    ("In-house staff", "In-house staff"),
    ("Contractor", "Contractor"),
    ("Other DoD Organization", "Other DoD Organization"),
    ("None", "None"),
]

DATA_TRANSFER_AMOUNTS = [
    ("", "Select an option"),
    ("Less than 100GB", "Less than 100GB"),
    ("100GB-500GB", "100GB-500GB"),
    ("500GB-1TB", "500GB-1TB"),
    ("1TB-50TB", "1TB-50TB"),
    ("50TB-100TB", "50TB-100TB"),
    ("100TB-500TB", "100TB-500TB"),
    ("500TB-1PB", "500TB-1PB"),
    ("1PB-5PB", "1PB-5PB"),
    ("5PB-10PB", "5PB-10PB"),
    ("Above 10PB", "Above 10PB"),
]

COMPLETION_DATE_RANGES = [
    ("", "Select an option"),
    ("Less than 1 month", "Less than 1 month"),
    ("1-3 months", "1-3 months"),
    ("3-6 months", "3-6 months"),
    ("Above 12 months", "Above 12 months"),
]

WORKSPACE_ROLES = [
    (
        "owner",
        {
            "name": "Workspace Owner",
            "description": "Adds, edits, deactivates access to all projects, environments, and members. Views budget reports. Initiates and edits JEDI Cloud requests.",
        },
    ),
    (
        "admin",
        {
            "name": "Administrator",
            "description": "Adds and edits projects, environments, members, but cannot deactivate. Cannot view budget reports or JEDI Cloud requests.",
        },
    ),
    (
        "developer",
        {
            "name": "Developer",
            "description": "Views only the projects and environments they are granted access to. Can also view members associated with each environment.",
        },
    ),
    (
        "billing_auditor",
        {
            "name": "Billing Auditor",
            "description": "Views only the projects and environments they are granted access to. Can also view budgets and reports associated with the workspace.",
        },
    ),
    (
        "security_auditor",
        {
            "name": "Security Auditor",
            "description": "Views only the projects and environments they are granted access to. Can also view activity logs.",
        },
    ),
]

ENVIRONMENT_ROLES = [
    (
        "developer",
        {
            "name": "Developer",
            "description": "Configures cloud-based IaaS and PaaS computing, networking, and storage services.",
        },
    ),
    (
        "database_administrator",
        {
            "name": "Database Administrator",
            "description": "Configures cloud-based database services.",
        },
    ),
    (
        "devops",
        {
            "name": "DevOps",
            "description": "Provisions, deprovisions, and deploys cloud-based IaaS and PaaS computing, networking, and storage services, including pre-configured machine images.",
        },
    ),
    (
        "billing_administrator",
        {
            "name": "Billing Administrator",
            "description": "Views cloud resource usage, budget reports, and invoices; Tracks budgets, including spend reports, cost planning and projections, and sets limits based on cloud service usage.",
        },
    ),
    (
        "security_administrator",
        {
            "name": "Security Administrator",
            "description": "Accesses information security and control tools of cloud resources which include viewing cloud resource usage logging, user roles and permissioning history.",
        },
    ),
    (
        "financial_auditor",
        {
            "name": "Financial Auditor",
            "description": "Views cloud resource usage and budget reports.",
        },
    ),
]

FUNDING_TYPES = [
    ("", "- Select -"),
    ("RDTE", "Research, Development, Testing & Evaluation (RDT&E)"),
    ("OM", "Operations & Maintenance (O&M)"),
    ("PROC", "Procurement (PROC)"),
    ("OTHER", "Other"),
]

TASK_ORDER_SOURCES = [("MANUAL", "Manual"), ("EDA", "EDA")]
