from datetime import date, timedelta

from app.database import SessionLocal, Base, engine
from app.models import (
    User,
    UserRole,
    Client,
    ServiceType,
    TaskTemplate,
    Engagement,
    Task,
    EngagementType,
    TaskStatus,
)
from app.auth import hash_password


Base.metadata.create_all(bind=engine)


def seed_data():
    db = SessionLocal()

    try:
        # =========================================================
        # 1. USERS
        # =========================================================

        users_data = [
            {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "admin123",
                "role": UserRole.ADMIN.value,
            },
            {
                "name": "Manager One",
                "email": "manager1@example.com",
                "password": "manager123",
                "role": UserRole.MANAGER.value,
            },
            {
                "name": "Manager Two",
                "email": "manager2@example.com",
                "password": "manager123",
                "role": UserRole.MANAGER.value,
            },
            {
                "name": "Team Member One",
                "email": "member1@example.com",
                "password": "member123",
                "role": UserRole.TEAM_MEMBER.value,
            },
            {
                "name": "Team Member Two",
                "email": "member2@example.com",
                "password": "member123",
                "role": UserRole.TEAM_MEMBER.value,
            },
            {
                "name": "Team Member Three",
                "email": "member3@example.com",
                "password": "member123",
                "role": UserRole.TEAM_MEMBER.value,
            },
            {
                "name": "Team Member Four",
                "email": "member4@example.com",
                "password": "member123",
                "role": UserRole.TEAM_MEMBER.value,
            },
        ]

        users = {}

        for user_data in users_data:
            existing_user = (
                db.query(User)
                .filter(User.email == user_data["email"])
                .first()
            )

            if existing_user:
                # Make sure demo users are active
                existing_user.is_active = True
                users[user_data["email"]] = existing_user

                print(
                    f"User already exists: "
                    f"{user_data['email']}"
                )

            else:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=hash_password(
                        user_data["password"]
                    ),
                    role=user_data["role"],
                    is_active=True,
                )

                db.add(user)
                db.flush()

                users[user_data["email"]] = user

                print(
                    f"Created user: "
                    f"{user_data['email']}"
                )

        db.commit()


        # =========================================================
        # 2. CLIENTS
        # =========================================================

        clients_data = [
            {
                "name": "ABC Consulting",
                "email": "contact@abcconsulting.example.com",
                "phone": "9876500001",
            },
            {
                "name": "XYZ Solutions",
                "email": "contact@xyzsolutions.example.com",
                "phone": "9876500002",
            },
            {
                "name": "Delhi Business Group",
                "email": "contact@delhibusiness.example.com",
                "phone": "9876500003",
            },
            {
                "name": "NorthStar Enterprises",
                "email": "contact@northstar.example.com",
                "phone": "9876500004",
            },
            {
                "name": "GreenLeaf Industries",
                "email": "contact@greenleaf.example.com",
                "phone": "9876500005",
            },
        ]

        clients = {}

        for client_data in clients_data:

            client = (
                db.query(Client)
                .filter(
                    Client.email == client_data["email"]
                )
                .first()
            )

            if client:
                clients[client_data["email"]] = client

                print(
                    f"Client already exists: "
                    f"{client_data['name']}"
                )

            else:
                client = Client(
                    name=client_data["name"],
                    email=client_data["email"],
                    phone=client_data["phone"],
                    is_active=True,
                )

                db.add(client)
                db.flush()

                clients[client_data["email"]] = client

                print(
                    f"Created client: "
                    f"{client_data['name']}"
                )

        db.commit()


        # =========================================================
        # 3. SERVICE TYPES
        # =========================================================

        services_data = [
            {
                "name": "Monthly Accounting",
                "description": (
                    "Monthly bookkeeping and accounting services."
                ),
                "engagement_type": EngagementType.RECURRING.value,
            },
            {
                "name": "Tax Filing",
                "description": (
                    "Tax preparation and filing services."
                ),
                "engagement_type": EngagementType.ONE_TIME.value,
            },
            {
                "name": "Audit",
                "description": (
                    "Financial audit and compliance services."
                ),
                "engagement_type": EngagementType.ONE_TIME.value,
            },
        ]

        services = {}

        for service_data in services_data:

            service = (
                db.query(ServiceType)
                .filter(
                    ServiceType.name == service_data["name"]
                )
                .first()
            )

            if service:
                services[service_data["name"]] = service

                print(
                    f"Service already exists: "
                    f"{service_data['name']}"
                )

            else:
                service = ServiceType(
                    name=service_data["name"],
                    description=service_data["description"],
                    engagement_type=service_data[
                        "engagement_type"
                    ],
                    is_active=True,
                )

                db.add(service)
                db.flush()

                services[service_data["name"]] = service

                print(
                    f"Created service: "
                    f"{service_data['name']}"
                )

        db.commit()


        # =========================================================
        # 4. TASK TEMPLATES
        # =========================================================

        templates_data = {
            "Monthly Accounting": [
                {
                    "name": "Collect Financial Documents",
                    "description": (
                        "Collect invoices, receipts and "
                        "financial documents."
                    ),
                    "default_days": 5,
                    "sequence": 1,
                },
                {
                    "name": "Bank Reconciliation",
                    "description": (
                        "Reconcile bank transactions."
                    ),
                    "default_days": 10,
                    "sequence": 2,
                },
                {
                    "name": "Prepare Monthly Reports",
                    "description": (
                        "Prepare monthly financial reports."
                    ),
                    "default_days": 20,
                    "sequence": 3,
                },
                {
                    "name": "Manager Review",
                    "description": (
                        "Review completed accounting work."
                    ),
                    "default_days": 25,
                    "sequence": 4,
                },
            ],
            "Tax Filing": [
                {
                    "name": "Collect Tax Documents",
                    "description": (
                        "Collect required tax documents."
                    ),
                    "default_days": 5,
                    "sequence": 1,
                },
                {
                    "name": "Prepare Tax Return",
                    "description": (
                        "Prepare the tax return."
                    ),
                    "default_days": 15,
                    "sequence": 2,
                },
                {
                    "name": "Tax Review",
                    "description": (
                        "Review the prepared tax return."
                    ),
                    "default_days": 20,
                    "sequence": 3,
                },
            ],
            "Audit": [
                {
                    "name": "Collect Audit Documents",
                    "description": (
                        "Collect documents required for audit."
                    ),
                    "default_days": 5,
                    "sequence": 1,
                },
                {
                    "name": "Perform Audit",
                    "description": (
                        "Perform audit procedures."
                    ),
                    "default_days": 15,
                    "sequence": 2,
                },
                {
                    "name": "Prepare Audit Report",
                    "description": (
                        "Prepare the final audit report."
                    ),
                    "default_days": 25,
                    "sequence": 3,
                },
            ],
        }

        service_templates = {}

        for service_name, template_list in templates_data.items():

            service = services[service_name]

            service_templates[service_name] = []

            for template_data in template_list:

                template = (
                    db.query(TaskTemplate)
                    .filter(
                        TaskTemplate.service_type_id
                        == service.id,
                        TaskTemplate.name
                        == template_data["name"],
                    )
                    .first()
                )

                if template:
                    service_templates[
                        service_name
                    ].append(template)

                    print(
                        f"Template already exists: "
                        f"{template_data['name']}"
                    )

                else:
                    template = TaskTemplate(
                        service_type_id=service.id,
                        name=template_data["name"],
                        description=template_data[
                            "description"
                        ],
                        default_days=template_data[
                            "default_days"
                        ],
                        sequence=template_data[
                            "sequence"
                        ],
                        is_active=True,
                    )

                    db.add(template)
                    db.flush()

                    service_templates[
                        service_name
                    ].append(template)

                    print(
                        f"Created template: "
                        f"{template_data['name']}"
                    )

        db.commit()


        # =========================================================
        # 5. CREATE 5 DEMO ENGAGEMENTS
        #    Each engagement gets 4 tasks
        #    Total = 20 tasks
        # =========================================================

        team_members = [
            users["member1@example.com"],
            users["member2@example.com"],
            users["member3@example.com"],
            users["member4@example.com"],
        ]

        demo_engagements = [
            {
                "client_email":
                    "contact@abcconsulting.example.com",
                "name":
                    "ABC Consulting - November 2026 Accounting",
                "start":
                    date(2026, 11, 1),
                "end":
                    date(2026, 11, 30),
                "due":
                    date(2026, 11, 30),
            },
            {
                "client_email":
                    "contact@xyzsolutions.example.com",
                "name":
                    "XYZ Solutions - December 2026 Accounting",
                "start":
                    date(2026, 12, 1),
                "end":
                    date(2026, 12, 31),
                "due":
                    date(2026, 12, 31),
            },
            {
                "client_email":
                    "contact@delhibusiness.example.com",
                "name":
                    "Delhi Business Group - January 2027 Accounting",
                "start":
                    date(2027, 1, 1),
                "end":
                    date(2027, 1, 31),
                "due":
                    date(2027, 1, 31),
            },
            {
                "client_email":
                    "contact@northstar.example.com",
                "name":
                    "NorthStar Enterprises - February 2027 Accounting",
                "start":
                    date(2027, 2, 1),
                "end":
                    date(2027, 2, 28),
                "due":
                    date(2027, 2, 28),
            },
            {
                "client_email":
                    "contact@greenleaf.example.com",
                "name":
                    "GreenLeaf Industries - March 2027 Accounting",
                "start":
                    date(2027, 3, 1),
                "end":
                    date(2027, 3, 31),
                "due":
                    date(2027, 3, 31),
            },
        ]


        task_number = 0

        for engagement_data in demo_engagements:

            client = clients[
                engagement_data["client_email"]
            ]

            service = services[
                "Monthly Accounting"
            ]

            # Check duplicate engagement
            existing_engagement = (
                db.query(Engagement)
                .filter(
                    Engagement.client_id == client.id,
                    Engagement.service_type_id
                    == service.id,
                    Engagement.period_start
                    == engagement_data["start"],
                    Engagement.period_end
                    == engagement_data["end"],
                )
                .first()
            )

            if existing_engagement:

                engagement = existing_engagement

                print(
                    f"Engagement already exists: "
                    f"{engagement.name}"
                )

            else:

                engagement = Engagement(
                    client_id=client.id,
                    service_type_id=service.id,
                    name=engagement_data["name"],
                    period_start=engagement_data["start"],
                    period_end=engagement_data["end"],
                    due_date=engagement_data["due"],
                    status="OPEN",
                )

                db.add(engagement)
                db.flush()

                print(
                    f"Created engagement: "
                    f"{engagement.name}"
                )


            # =====================================================
            # CREATE TASKS FROM MONTHLY ACCOUNTING TEMPLATES
            # =====================================================

            templates = service_templates[
                "Monthly Accounting"
            ]

            for template in templates:

                existing_task = (
                    db.query(Task)
                    .filter(
                        Task.engagement_id
                        == engagement.id,
                        Task.title
                        == template.name,
                    )
                    .first()
                )

                if existing_task:

                    print(
                        f"Task already exists: "
                        f"{existing_task.title}"
                    )

                    continue

                task_number += 1

                task_due_date = (
                    engagement_data["start"]
                    + timedelta(
                        days=template.default_days
                    )
                )

                if task_due_date > engagement_data["due"]:
                    task_due_date = engagement_data["due"]

                assigned_member = team_members[
                    (task_number - 1)
                    % len(team_members)
                ]

                task = Task(
                    engagement_id=engagement.id,
                    assigned_to_id=assigned_member.id,
                    created_by_id=users[
                        "admin@example.com"
                    ].id,
                    title=template.name,
                    description=template.description,
                    status=TaskStatus.NOT_STARTED.value,
                    due_date=task_due_date,
                )

                db.add(task)

                print(
                    f"Created task: "
                    f"{template.name} "
                    f"-> {assigned_member.name}"
                )


        db.commit()


        # =========================================================
        # 6. FINAL SUMMARY
        # =========================================================

        total_users = db.query(User).count()
        total_clients = db.query(Client).count()
        total_services = db.query(ServiceType).count()
        total_templates = db.query(TaskTemplate).count()
        total_engagements = db.query(Engagement).count()
        total_tasks = db.query(Task).count()

        print("\n========================================")
        print("SEED DATA COMPLETED")
        print("========================================")
        print(f"Users:        {total_users}")
        print(f"Clients:      {total_clients}")
        print(f"Services:     {total_services}")
        print(f"Templates:    {total_templates}")
        print(f"Engagements:  {total_engagements}")
        print(f"Tasks:        {total_tasks}")
        print("========================================")

        print("\nDemo Login Credentials")
        print("----------------------------------------")
        print("Admin:")
        print("admin@example.com / admin123")
        print()
        print("Manager 1:")
        print("manager1@example.com / manager123")
        print()
        print("Manager 2:")
        print("manager2@example.com / manager123")
        print()
        print("Team Member 1:")
        print("member1@example.com / member123")
        print()
        print("Team Member 2:")
        print("member2@example.com / member123")
        print()
        print("Team Member 3:")
        print("member3@example.com / member123")
        print()
        print("Team Member 4:")
        print("member4@example.com / member123")
        print("----------------------------------------")


    except Exception as error:

        db.rollback()

        print("\nERROR WHILE SEEDING DATA:")
        print(error)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()