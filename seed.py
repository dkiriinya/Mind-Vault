"""Database seed script for demo & presentation purposes.

Populates MindVault with realistic Kenyan university coursework,
vault materials (M-Pesa Daraja 2.0 API, Distributed Systems in East Africa,
Banker's Algorithm in Core Banking, Mobile Money DB indexing),
AI Study Assistant guides, 3D flashcards, quizzes, group tasks,
and live conversational Q&A threads.

Automatically seeds for:
  • demo@mindvault.co.ke (Primary Kenyan presentation account)
  • demo@mindvault.edu (Secondary presentation account)
  • Any logged-in / existing user in the database (e.g. don@dgktech.co.ke)

Run via:
    python seed.py
"""
import os
import sys
from datetime import date, timedelta

# Initialize Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
import django

django.setup()

from django.contrib.auth import get_user_model
from apps.vault.models import Semester, Course, Unit, Tag, Material
from apps.sharing.models import StudyGroup, Membership
from apps.study_assistant.models import (
    StudyDocument,
    GeneratedNote,
    Flashcard,
    QuizQuestion,
    GroupStudyResource,
    GroupSessionTask,
    StudyChatMessage,
)

User = get_user_model()


def seed_user_curriculum(user, university_name="Strathmore University"):
    """Populate full Kenyan academic curriculum, vault materials, and AI study resources for a user."""
    print(f"\n📂 Seeding Kenyan curriculum for: {user.email} ({user.full_name or 'Student'})...")

    if not user.university:
        user.university = university_name
        user.save(update_fields=["university"])

    # 1. Semesters (Kenyan Academic System)
    sem_current, _ = Semester.objects.get_or_create(
        owner=user,
        name="Year 3 Semester 1 (2026/2027)",
    )
    sem_previous, _ = Semester.objects.get_or_create(
        owner=user,
        name="Year 2 Semester 2 (2025/2026)",
    )

    # 2. Courses (Kenyan Computer Science & IT Curriculum)
    c_fintech, _ = Course.objects.get_or_create(
        semester=sem_current,
        title="Mobile Financial Technologies & Daraja API Architecture",
        defaults={"code": "BIT 3205"},
    )
    c_dist, _ = Course.objects.get_or_create(
        semester=sem_current,
        title="Distributed Systems & Cloud Infrastructure",
        defaults={"code": "ICS 3101"},
    )
    c_os, _ = Course.objects.get_or_create(
        semester=sem_previous,
        title="Operating Systems & Kernel Architecture",
        defaults={"code": "ICS 2204"},
    )
    c_db, _ = Course.objects.get_or_create(
        semester=sem_previous,
        title="Database Systems Design & Query Optimization",
        defaults={"code": "BBIT 2108"},
    )

    # 3. Units
    u_daraja, _ = Unit.objects.get_or_create(course=c_fintech, title="Unit 1: M-Pesa Daraja 2.0 Integration & STK Push", defaults={"order": 1})
    u_recon, _ = Unit.objects.get_or_create(course=c_fintech, title="Unit 2: Financial Reconciliation & Idempotency", defaults={"order": 2})
    u_raft, _ = Unit.objects.get_or_create(course=c_dist, title="Unit 1: Consensus Protocols in Low-Latency Data Centers", defaults={"order": 1})
    u_deadlock, _ = Unit.objects.get_or_create(course=c_os, title="Unit 1: Concurrency, Deadlocks & Banker's Algorithm", defaults={"order": 1})
    u_btree, _ = Unit.objects.get_or_create(course=c_db, title="Unit 1: High-Throughput Indexing in Mobile Wallets", defaults={"order": 1})

    # 4. Tags
    tag_kenya, _ = Tag.objects.get_or_create(owner=user, name="Kenyan Tech")
    tag_fintech, _ = Tag.objects.get_or_create(owner=user, name="M-Pesa & Fintech")
    tag_systems, _ = Tag.objects.get_or_create(owner=user, name="Systems Architecture")
    tag_midterm, _ = Tag.objects.get_or_create(owner=user, name="Midterm Exam Prep")

    # 5. Vault Materials (Kenyan Market Focused)
    mat_daraja, _ = Material.objects.get_or_create(
        owner=user,
        unit=u_daraja,
        title="M-Pesa Daraja 2.0 API Architecture & STK Push Integration",
        defaults={
            "kind": Material.Kind.NOTE,
            "sensitivity": Material.Sensitivity.INTERNAL,
            "notes": (
                "Safaricom's Daraja 2.0 gateway enables merchant integration for mobile payments across East Africa.\n\n"
                "1. Authentication Workflow:\n"
                "- Endpoint: https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials\n"
                "- Sends HTTP Basic Auth header: Base64(ConsumerKey:ConsumerSecret).\n"
                "- Returns OAuth Bearer token valid for 3,599 seconds (~1 hour).\n\n"
                "2. Lipa na M-Pesa Online (STK Push / C2B):\n"
                "- Endpoint: /mpesa/stkpush/v1/processrequest\n"
                "- Required Payload Headers: Bearer <token>\n"
                "- Password computation: Base64.encode(BusinessShortCode + PassKey + Timestamp[YYYYMMDDHHmmss]).\n"
                "- Phone Number format: International format without plus or spaces (e.g. 254712345678 or 254112345678).\n"
                "- CallBackURL: Secure public HTTPS URL where Safaricom pushes the asynchronous payment response.\n\n"
                "3. Asynchronous Webhook Callbacks:\n"
                "- ResultCode 0: Success (funds transferred, PIN accepted).\n"
                "- ResultCode 1032: Canceled by user (dismissed prompt or clicked Cancel).\n"
                "- ResultCode 1: Insufficient funds in subscriber wallet.\n"
                "- ResultCode 2001: Wrong M-Pesa PIN entered.\n\n"
                "4. Resiliency & Idempotency Invariants:\n"
                "- Always respond to the callback with HTTP 200: {'ResultCode': 0, 'ResultDesc': 'Accepted'}.\n"
                "- Track transactions using CheckoutRequestID and MpesaReceiptNumber.\n"
                "- Use database locks on user wallets to prevent duplicate crediting when Safaricom retries webhooks."
            ),
        },
    )
    mat_daraja.tags.add(tag_kenya, tag_fintech, tag_midterm)

    mat_raft, _ = Material.objects.get_or_create(
        owner=user,
        unit=u_raft,
        title="Raft Consensus & Distributed Fault Tolerance in Kenyan Cloud Clusters",
        defaults={
            "kind": Material.Kind.NOTE,
            "sensitivity": Material.Sensitivity.INTERNAL,
            "notes": (
                "Fault-tolerant clustering between East African cloud nodes (Nairobi ADC, Mombasa IXP, and Eldoret nodes).\n"
                "Raft decomposes consensus into three independent subproblems:\n"
                "1. Leader Election: Follower, Candidate, Leader states governed by randomized timers (150ms-300ms).\n"
                "2. Log Replication: Unidirectional flow from Leader to Followers; majority quorum (floor(N/2) + 1).\n"
                "3. Safety Invariants: Subsea cable cuts resilience (TEAMS, SEACOM) and WAN partitioning behavior."
            ),
        },
    )
    mat_raft.tags.add(tag_kenya, tag_systems)

    mat_deadlock, _ = Material.objects.get_or_create(
        owner=user,
        unit=u_deadlock,
        title="Deadlock Prevention & Banker's Algorithm in Core Banking Engines",
        defaults={
            "kind": Material.Kind.NOTE,
            "sensitivity": Material.Sensitivity.INTERNAL,
            "notes": (
                "Deadlock analysis in transaction processing systems (KRA iTax & Kenyan inter-bank Pesalink / RTGS).\n"
                "All 4 Coffman conditions must hold simultaneously: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.\n"
                "Banker's Algorithm determines whether resource requests leave the banking ledger in a provably safe state."
            ),
        },
    )
    mat_deadlock.tags.add(tag_kenya, tag_systems)

    mat_db, _ = Material.objects.get_or_create(
        owner=user,
        unit=u_btree,
        title="High-Throughput Mobile Money Database Indexing (PostgreSQL & Redis)",
        defaults={
            "kind": Material.Kind.RESEARCH,
            "sensitivity": Material.Sensitivity.PUBLIC,
            "authors": "Eng. Mwangi Karanja, Dr. Faith Wanjiku",
            "publication_year": 2025,
            "notes": (
                "Empirical benchmarking of PostgreSQL B-Tree indexes versus LSM-Tree storage (RocksDB) "
                "under peak Kenyan holiday transaction volumes (over 3,000 TPS on Safaricom M-Pesa channels).\n"
                "Includes read/write amplification metrics, table partitioning by monthly fiscal periods, and Redis caching."
            ),
        },
    )
    mat_db.tags.add(tag_kenya, tag_fintech)

    # 6. Study Group
    group, _ = StudyGroup.objects.get_or_create(
        name="Nairobi Tech & Systems Innovators",
        defaults={"owner": user},
    )
    Membership.objects.get_or_create(group=group, user=user, defaults={"role": Membership.Role.OWNER})

    # 7. AI Study Assistant Document & Resources (Focusing on M-Pesa Daraja 2.0 Integration)
    doc, _ = StudyDocument.objects.get_or_create(
        user=user,
        material=mat_daraja,
        title="M-Pesa Daraja 2.0 API Architecture & STK Push Integration",
        defaults={
            "group": group,
            "status": StudyDocument.Status.COMPLETED,
            "extracted_text": mat_daraja.notes,
            "raw_text": mat_daraja.notes,
        },
    )

    # Generated Notes
    GeneratedNote.objects.update_or_create(
        document=doc,
        defaults={
            "summary": (
                "Safaricom Daraja 2.0 provides RESTful API endpoints for mobile payment automation in Kenya. "
                "The Lipa na M-Pesa Online (STK Push) workflow enables automated SIM toolkit checkout prompts, "
                "relying on OAuth 2.0 Bearer tokens, encrypted transaction passwords, and asynchronous webhook callbacks."
            ),
            "explanation": (
                "In modern Kenyan software architectures, processing customer payments requires separating the initiation "
                "handshake from transaction completion. When an STK Push is dispatched, Safaricom's gateway immediately replies "
                "with an acknowledgment containing a CheckoutRequestID. The actual debit occurs asynchronously on the subscriber's "
                "phone. Upon PIN verification, Safaricom delivers an encrypted webhook payload to the merchant's CallBackURL. "
                "Developers must enforce idempotent ledger updates using database transaction locks to guarantee that network "
                "callback retries never result in double crediting or duplicate orders."
            ),
            "structured_notes": [
                "Authentication: Generate OAuth Bearer token by dispatching HTTP Basic Auth with Base64(ConsumerKey:ConsumerSecret) to /oauth/v1/generate.",
                "STK Password: Formulated strictly as Base64.encode(BusinessShortCode + PassKey + YYYYMMDDHHmmss).",
                "MSISDN Formatting: Phone numbers must be formatted in Kenyan international standard without spaces or pluses (e.g. 254712345678).",
                "Callback Lifecycle: ResultCode 0 signifies verified payment; ResultCode 1032 indicates subscriber cancellation.",
                "Idempotency Guarantee: Maintain database uniqueness on CheckoutRequestID and MpesaReceiptNumber within an atomic transaction.",
            ],
        },
    )

    # Flashcards (5 high-yield 3D flashcards for the presentation)
    doc.flashcards.all().delete()
    Flashcard.objects.bulk_create([
        Flashcard(
            document=doc,
            question="What is the exact formula for computing the Safaricom Daraja STK Push password?",
            answer="Base64.encode(BusinessShortCode + PassKey + Timestamp[YYYYMMDDHHmmss])",
            order=0,
        ),
        Flashcard(
            document=doc,
            question="What telephone number format is required by Daraja for PartyA and PhoneNumber?",
            answer="The Kenyan international format without plus or symbols (e.g. 2547XXXXXXXX or 2541XXXXXXXX).",
            order=1,
        ),
        Flashcard(
            document=doc,
            question="What does an asynchronous callback ResultCode of 1032 signify?",
            answer="The payment request was canceled by the subscriber (e.g. they dismissed the STK prompt or clicked Cancel).",
            order=2,
        ),
        Flashcard(
            document=doc,
            question="Why should a merchant system never credit a user balance based solely on the initial STK Push HTTP response?",
            answer="The initial HTTP response only confirms prompt queueing at Safaricom; actual funds movement is only confirmed via the asynchronous webhook callback with ResultCode 0.",
            order=3,
        ),
        Flashcard(
            document=doc,
            question="What unique identifier pairs are used to correlate an initial STK Push request with its asynchronous callback?",
            answer="The CheckoutRequestID and MerchantRequestID returned in the initiation response.",
            order=4,
        ),
    ])

    # Quizzes (3 multiple-choice questions)
    doc.quiz_questions.all().delete()
    QuizQuestion.objects.bulk_create([
        QuizQuestion(
            document=doc,
            question="Which Daraja callback ResultCode indicates a successfully processed payment?",
            options=[
                "A) ResultCode 0",
                "B) ResultCode 1",
                "C) ResultCode 1032",
                "D) ResultCode 2001",
            ],
            correct_answer="A) ResultCode 0",
            explanation="ResultCode 0 signals that the subscriber entered their M-Pesa PIN correctly and the payment transfer succeeded.",
            order=0,
        ),
        QuizQuestion(
            document=doc,
            question="If your server receives duplicate webhook callbacks from Safaricom due to network retries, how should you handle it?",
            options=[
                "A) Return an HTTP 500 error to Safaricom",
                "B) Implement idempotency checking on CheckoutRequestID and MpesaReceiptNumber inside a database transaction",
                "C) Double credit the subscriber's account",
                "D) Shut down the webhook endpoint",
            ],
            correct_answer="B) Implement idempotency checking on CheckoutRequestID and MpesaReceiptNumber inside a database transaction",
            explanation="Idempotent design verifies whether the transaction has already been fulfilled, safely acknowledging repeated retries without double crediting.",
            order=1,
        ),
        QuizQuestion(
            document=doc,
            question="What grant_type parameter must be passed when requesting an OAuth token from Daraja?",
            options=[
                "A) authorization_code",
                "B) client_credentials",
                "C) password",
                "D) refresh_token",
            ],
            correct_answer="B) client_credentials",
            explanation="Daraja uses standard client_credentials grant type authenticated via Consumer Key and Consumer Secret.",
            order=2,
        ),
    ])

    # Group Study Resource & Tasks
    group_res, _ = GroupStudyResource.objects.update_or_create(
        document=doc,
        defaults={
            "revision_summary": (
                "Group study priority: Deep dive into Safaricom Daraja 2.0 production deployment, "
                "handling webhook network timeouts, KRA eTIMS invoice generation, and automated daily reconciliation."
            ),
            "material_conflicts": [
                "Daraja sandbox documentation specifies callback delivery within 10 to 30 seconds, but live Safaricom gateway logs indicate edge-case queuing delays of up to 60-90 seconds during peak hours.",
                "Tutorial notes recommend polling the Transaction Status Query immediately after 30 seconds, while Safaricom engineering guidelines mandate a minimum 2-minute cooling interval.",
            ],
            "unanswered_queries": [
                "How should our Django backend recover when an intermittent AWS/DigitalOcean network partition causes our webhook to miss Safaricom's 3 callback retries?",
                "What is the recommended encryption standard for storing M-Pesa PassKeys securely in production Django environment configurations?",
            ],
        },
    )

    group_res.tasks.all().delete()
    GroupSessionTask.objects.bulk_create([
        GroupSessionTask(
            resource=group_res,
            title="Set up Safaricom Daraja 2.0 Sandbox and register test credentials",
            description="Acquire Consumer Key, Consumer Secret, and Passkey from the developer portal.",
            is_completed=True,
            due_date=date.today() - timedelta(days=2),
        ),
        GroupSessionTask(
            resource=group_res,
            title="Implement Django webhook receiver for Lipa na M-Pesa callbacks",
            description="Build POST handler with JSON parsing, ResultCode 0 validation, and HTTP 200 acknowledgment.",
            is_completed=True,
            due_date=date.today() - timedelta(days=1),
        ),
        GroupSessionTask(
            resource=group_res,
            title="Build automated ledger reconciliation script against M-Pesa Excel statements",
            description="Match CheckoutRequestIDs with internal database payment entries.",
            is_completed=False,
            due_date=date.today() + timedelta(days=3),
        ),
        GroupSessionTask(
            resource=group_res,
            title="Review KRA eTIMS compliance hooks for instant digital receipts",
            description="Prepare architecture overview for generating compliant cryptographically signed invoices.",
            is_completed=False,
            due_date=date.today() + timedelta(days=5),
        ),
    ])

    # Conversational Q&A Thread (Chat with Material)
    doc.chat_messages.all().delete()
    StudyChatMessage.objects.bulk_create([
        StudyChatMessage(
            document=doc,
            role=StudyChatMessage.Role.USER,
            content="How does the STK Push authentication work in Daraja 2.0?",
        ),
        StudyChatMessage(
            document=doc,
            role=StudyChatMessage.Role.ASSISTANT,
            content=(
                "In Safaricom Daraja 2.0, STK Push uses a two-tier authentication architecture:\n\n"
                "1. **OAuth 2.0 Bearer Token**: Your backend calls `https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials` "
                "passing `ConsumerKey:ConsumerSecret` base64-encoded in the HTTP `Authorization: Basic` header. Safaricom returns an access token valid for 3,599 seconds (~1 hour).\n\n"
                "2. **Encrypted Transaction Password**: In the STK request body, you provide a dynamic `Password` field calculated as:\n"
                "```python\n"
                "password = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()\n"
                "```\n"
                "Safaricom verifies this password and timestamp on the fly to prevent replay attacks!\n\n"
                "Would you like an example of the complete Python request function?"
            ),
        ),
        StudyChatMessage(
            document=doc,
            role=StudyChatMessage.Role.USER,
            content="What happens if a user enters the wrong M-Pesa PIN on their phone?",
        ),
        StudyChatMessage(
            document=doc,
            role=StudyChatMessage.Role.ASSISTANT,
            content=(
                "When a subscriber enters the wrong M-Pesa PIN on their phone prompt:\n\n"
                "1. Safaricom alerts them on their SIM toolkit to retry or cancel.\n"
                "2. If the transaction terminates, Safaricom delivers a webhook callback to your `CallBackURL` with:\n"
                "   • `ResultCode`: `2001` (Wrong PIN entered) or `1032` (User cancelled the STK prompt)\n"
                "   • `ResultDesc`: Descriptive notification, e.g. *'The initiator information is invalid'*\n\n"
                "Your backend should check `if result_code != 0`, update the pending order status to 'Failed' or 'Canceled', "
                "and display an actionable prompt on your frontend asking the user to re-attempt payment with the correct PIN!"
            ),
        ),
    ])

    print(f"  ✓ {user.email}: 4 Courses, 5 Units, 4 Materials, Study Group, Flashcards, Quizzes, and Q&A Chat ready!")


def seed():
    print("=" * 65)
    print("🇰🇪  Seeding MindVault Data (Kenyan University & Tech Market)...")
    print("=" * 65)

    # 1. Primary Kenyan presentation account
    user_ke, _ = User.objects.get_or_create(
        email="demo@mindvault.co.ke",
        defaults={
            "full_name": "Brian Kiprop",
            "university": "Strathmore University",
        },
    )
    user_ke.set_password("Password123!")
    user_ke.full_name = "Brian Kiprop"
    user_ke.university = "Strathmore University"
    user_ke.save()

    # 2. Secondary Kenyan presentation account
    user_edu, _ = User.objects.get_or_create(
        email="demo@mindvault.edu",
        defaults={
            "full_name": "Mwangi Karanja",
            "university": "University of Nairobi (UoN)",
        },
    )
    user_edu.set_password("Password123!")
    user_edu.full_name = "Mwangi Karanja"
    user_edu.university = "University of Nairobi (UoN)"
    user_edu.save()

    # 3. Classmate peer account
    peer, _ = User.objects.get_or_create(
        email="faith.wanjiku@strathmore.edu",
        defaults={
            "full_name": "Faith Wanjiku",
            "university": "Strathmore University",
        },
    )
    peer.set_password("Password123!")
    peer.save()

    # Seed for all users currently in the database (ensuring whichever user is logged in has full data!)
    all_users = User.objects.all()
    for u in all_users:
        uni = "Strathmore University" if "co.ke" in u.email else "University of Nairobi"
        seed_user_curriculum(u, university_name=uni)

    print("\n" + "=" * 65)
    print("🎉  Kenyan Market Database Seeding Completed Successfully!")
    print("=" * 65)
    print("Ready Accounts for Presentation:")
    print("  1. Primary Kenyan Account:")
    print("     • Email:    demo@mindvault.co.ke")
    print("     • Password: Password123!")
    print("     • Name:     Brian Kiprop (Strathmore University)")
    print("\n  2. Secondary Account:")
    print("     • Email:    demo@mindvault.edu")
    print("     • Password: Password123!")
    print("     • Name:     Mwangi Karanja (University of Nairobi)")

    other_users = [u.email for u in all_users if u.email not in ("demo@mindvault.co.ke", "demo@mindvault.edu", "faith.wanjiku@strathmore.edu")]
    if other_users:
        print("\n  3. Also seeded for your existing logged-in accounts:")
        for o in other_users:
            print(f"     • {o}")

    print("\nPresentation Quick Links:")
    print("  • AI Study Assistant:  http://127.0.0.1:8000/study-assistant/")
    print("  • Material Library:    http://127.0.0.1:8000/vault/materials/")
    print("  • Dashboard:           http://127.0.0.1:8000/")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    seed()
