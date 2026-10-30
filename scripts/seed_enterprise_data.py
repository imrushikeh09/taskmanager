"""
Task Manager Pro - Enterprise Realistic Seed Data Script
Generates comprehensive projects, users, tasks, attachments, and notifications
mirroring a real-world Jira / Azure DevOps enterprise production environment.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from common.roles import UserRole
from projects.models import Project
from tasks.models import Task
from attachments.models import TaskAttachment
from notifications.models import Notification

User = get_user_model()

def seed():
    print("🚀 Seeding enterprise data into Task Manager database...")

    # Ensure RBAC Groups exist
    admin_group, _ = Group.objects.get_or_create(name=UserRole.ADMIN)
    viewer_group, _ = Group.objects.get_or_create(name=UserRole.VIEWER)

    # 1. Ensure Team Members exist
    admin_user, _ = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@taskmanager.pro", "is_superuser": True, "is_staff": True}
    )
    admin_user.set_password("admin123")
    admin_user.is_superuser = True
    admin_user.is_staff = True
    admin_user.groups.add(admin_group)
    admin_user.save()

    sarah, _ = User.objects.get_or_create(
        username="sarah.chen",
        defaults={"email": "sarah.chen@techcorp.com"}
    )
    sarah.set_password("user123")
    sarah.save()

    alex, _ = User.objects.get_or_create(
        username="alex.devops",
        defaults={"email": "alex.devops@techcorp.com"}
    )
    alex.set_password("user123")
    alex.save()

    priya, _ = User.objects.get_or_create(
        username="priya.qa",
        defaults={"email": "priya.qa@techcorp.com"}
    )
    priya.set_password("user123")
    priya.groups.add(viewer_group)
    priya.save()

    print("✅ Created 4 enterprise team members (admin, sarah.chen, alex.devops, priya.qa)")

    # 2. Enterprise Projects (Azure Boards / Jira style)
    p1, _ = Project.objects.get_or_create(
        name="Core Cloud Infrastructure & Kubernetes",
        defaults={
            "description": "Multi-region AWS EKS migration, Terraform IAC templates, and zero-downtime Nginx ingress setup.",
            "owner": admin_user,
        }
    )

    p2, _ = Project.objects.get_or_create(
        name="Payment Gateway & Billing Engine v2",
        defaults={
            "description": "Stripe/PayPal SCA compliant recurring billing, idempotency keys, and automated invoice PDF generation.",
            "owner": sarah,
        }
    )

    p3, _ = Project.objects.get_or_create(
        name="Customer Mobile App (React Native)",
        defaults={
            "description": "iOS and Android customer portal with biometric auth, push notifications, and offline caching.",
            "owner": admin_user,
        }
    )

    print("✅ Created 3 core enterprise projects")

    # 3. Tasks across all 4 statuses and priorities with realistic acceptance criteria
    today = date.today()
    
    tasks_data = [
        # --- Project 1: Cloud Infra ---
        {
            "project": p1,
            "title": "Configure EKS Multi-AZ Cluster & Least-Conn Load Balancer",
            "description": "Deploy Amazon EKS 1.30 across 3 availability zones with Nginx ingress controller using least_conn scheduling.",
            "priority": "URGENT",
            "status": "IN_PROGRESS",
            "assignee": alex,
            "creator": admin_user,
            "due_date": today + timedelta(days=2),
        },
        {
            "project": p1,
            "title": "Implement Redis Cluster Failover with Sentinel Replication",
            "description": "Configure 3 Redis nodes with Sentinel quorum = 2 to ensure zero message loss during Celery task execution.",
            "priority": "HIGH",
            "status": "TODO",
            "assignee": alex,
            "creator": admin_user,
            "due_date": today + timedelta(days=5),
        },
        {
            "project": p1,
            "title": "Audit SSL/TLS Ciphers and HSTS Preload Compliance",
            "description": "Upgrade TLS protocol support to 1.3 only, disable deprecated CBC ciphers, and verify A+ rating on Qualys SSL Labs.",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assignee": admin_user,
            "creator": admin_user,
            "due_date": today - timedelta(days=3),
        },
        {
            "project": p1,
            "title": "Resolve Database IOPS Saturation on PostgreSQL Replica",
            "description": "Disk write queue length spiked to 45. Investigate missing indexes on task_task.created_at and adjust shared_buffers.",
            "priority": "URGENT",
            "status": "BLOCKED",
            "assignee": alex,
            "creator": admin_user,
            "due_date": today + timedelta(days=1),
        },
        {
            "project": p1,
            "title": "Prometheus & Grafana Ingress Metrics Dashboard",
            "description": "Set up alerts for HTTP 5xx rate > 1% over 5-minute rolling window and Gunicorn worker saturation.",
            "priority": "LOW",
            "status": "TODO",
            "assignee": priya,
            "creator": alex,
            "due_date": today + timedelta(days=12),
        },

        # --- Project 2: Billing Engine ---
        {
            "project": p2,
            "title": "Stripe Webhook Signature Verification & Idempotency Key",
            "description": "Securely verify stripe-signature header using endpoint secret. Cache idempotency keys in Redis for 24h to prevent double charging.",
            "priority": "URGENT",
            "status": "IN_PROGRESS",
            "assignee": sarah,
            "creator": admin_user,
            "due_date": today + timedelta(days=3),
        },
        {
            "project": p2,
            "title": "Automated PDF Invoice Generation via Celery Worker",
            "description": "Dispatch background task upon invoice.paid event to compile PDF receipt and store on persistent media volume.",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assignee": sarah,
            "creator": sarah,
            "due_date": today - timedelta(days=1),
        },
        {
            "project": p2,
            "title": "Handle Currency Conversion for EUR and GBP Subscriptions",
            "description": "Integrate OpenExchangeRates API with hourly Redis caching for real-time FX rate settlement.",
            "priority": "MEDIUM",
            "status": "TODO",
            "assignee": sarah,
            "creator": admin_user,
            "due_date": today + timedelta(days=7),
        },
        {
            "project": p2,
            "title": "PCI-DSS Level 1 Compliance Self-Assessment Report",
            "description": "Review third-party tokenization flow to ensure no raw credit card numbers ever touch backend memory.",
            "priority": "HIGH",
            "status": "BLOCKED",
            "assignee": admin_user,
            "creator": admin_user,
            "due_date": today + timedelta(days=4),
        },

        # --- Project 3: Mobile App ---
        {
            "project": p3,
            "title": "Biometric Authentication (FaceID & Android Fingerprint)",
            "description": "Store refresh tokens in iOS Keychain / Android KeyStore using React Native Keychain library.",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "assignee": sarah,
            "creator": admin_user,
            "due_date": today + timedelta(days=6),
        },
        {
            "project": p3,
            "title": "Offline Task Draft Synchronization via WatermelonDB",
            "description": "Allow team members to create tasks offline in flights and sync delta changes when network re-establishes.",
            "priority": "MEDIUM",
            "status": "TODO",
            "assignee": sarah,
            "creator": admin_user,
            "due_date": today + timedelta(days=14),
        },
        {
            "project": p3,
            "title": "Apple App Store & Google Play Console Submission Review",
            "description": "Prepare app privacy nutrition labels, screenshots for iPad and iPhone 16 Pro, and release notes.",
            "priority": "LOW",
            "status": "TODO",
            "assignee": priya,
            "creator": admin_user,
            "due_date": today + timedelta(days=21),
        },
        {
            "project": p3,
            "title": "Push Notification Dispatch via Firebase Cloud Messaging",
            "description": "Wire Django Celery event to trigger FCM push notifications when user is tagged in a task comment.",
            "priority": "URGENT",
            "status": "COMPLETED",
            "assignee": alex,
            "creator": sarah,
            "due_date": today - timedelta(days=2),
        },
    ]

    for item in tasks_data:
        t, created = Task.objects.get_or_create(
            project=item["project"],
            title=item["title"],
            defaults={
                "description": item["description"],
                "priority": item["priority"],
                "status": item["status"],
                "assignee": item["assignee"],
                "creator": item["creator"],
                "due_date": item["due_date"],
            }
        )
        if not created:
            t.description = item["description"]
            t.priority = item["priority"]
            t.status = item["status"]
            t.assignee = item["assignee"]
            t.due_date = item["due_date"]
            t.save()

    print(f"✅ Seeded {len(tasks_data)} enterprise issues across all 4 statuses & priorities")

    # 4. Realistic In-App Notifications
    Notification.objects.all().delete()
    notifs_data = [
        {"recipient": admin_user, "notification_type": "SYSTEM_ALERT", "message": "Critical Alert: PostgreSQL IOPS spike detected on Replica-02.", "is_read": False},
        {"recipient": admin_user, "notification_type": "SYSTEM_ALERT", "message": "Nginx reverse proxy gateway deployed successfully to production.", "is_read": False},
        {"recipient": admin_user, "notification_type": "TASK_ASSIGNED", "message": "Sarah Chen assigned you to review Stripe Webhook idempotency caching.", "is_read": False},
        {"recipient": admin_user, "notification_type": "STATUS_CHANGED", "message": "Monthly subscription invoice #INV-2026-1049 status changed to COMPLETED.", "is_read": True},
        {"recipient": admin_user, "notification_type": "SYSTEM_ALERT", "message": "Engineering team Sprint 42 retrospective set for Friday at 16:00 UTC.", "is_read": True},
    ]

    for nd in notifs_data:
        Notification.objects.create(
            recipient=nd["recipient"],
            notification_type=nd["notification_type"],
            message=nd["message"],
            is_read=nd["is_read"],
        )

    print("✅ Seeded 5 in-app notifications (3 unread, 2 read)")
    print("🎉 All enterprise seed data successfully written to PostgreSQL!")

if __name__ == "__main__":
    seed()
