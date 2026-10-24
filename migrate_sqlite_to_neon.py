import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.db import transaction, connections, connection
from django.core.management.color import no_style
from apps.accounts.models import User
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
from django.contrib.sessions.models import Session

MODELS_ORDER = [
    User,
    Semester,
    Course,
    Unit,
    Tag,
    Material,
    StudyGroup,
    Membership,
    StudyDocument,
    GeneratedNote,
    Flashcard,
    QuizQuestion,
    GroupStudyResource,
    GroupSessionTask,
    StudyChatMessage,
    Session,
]

def migrate_data():
    print("=" * 60)
    print("🚀  Starting Complete Data Migration: SQLite -> Neon PostgreSQL")
    print("=" * 60)

    # 1. Clear existing application data in Neon in reverse dependency order
    print("\n1. Clearing existing target data in Neon PostgreSQL...")
    with transaction.atomic(using="default"):
        for model in reversed(MODELS_ORDER):
            count = model.objects.using("default").count()
            model.objects.using("default").all().delete()
            print(f"   Cleared {model._meta.label} ({count} existing records removed)")

        # Clear M2M table Material.tags.through
        through_model = Material.tags.through
        through_model.objects.using("default").all().delete()

    print("\n2. Migrating records from SQLite to Neon PostgreSQL...")
    with transaction.atomic(using="default"):
        for model in MODELS_ORDER:
            src_objs = list(model.objects.using("sqlite").all())
            if src_objs:
                model.objects.using("default").bulk_create(src_objs)
                print(f"   ✓ {model._meta.label}: {len(src_objs)} records migrated")
            else:
                print(f"   - {model._meta.label}: 0 records")

        # Migrate Material tags through table
        through_model = Material.tags.through
        through_objs = list(through_model.objects.using("sqlite").all())
        if through_objs:
            through_model.objects.using("default").bulk_create(through_objs)
            print(f"   ✓ {through_model._meta.label} (M2M): {len(through_objs)} relations migrated")

    print("\n3. Resetting PostgreSQL sequences for autoincrement primary keys...")
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), MODELS_ORDER + [Material.tags.through])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
    print("   ✓ PostgreSQL sequences reset successfully.")

    print("\n4. Verifying Migration Integrity:")
    all_matched = True
    for model in MODELS_ORDER:
        sqlite_count = model.objects.using("sqlite").count()
        neon_count = model.objects.using("default").count()
        status = "MATCH" if sqlite_count == neon_count else "MISMATCH!"
        if status != "MATCH":
            all_matched = False
        print(f"   • {model._meta.label:<35} SQLite: {sqlite_count:<4} | Neon: {neon_count:<4} [{status}]")

    through_sqlite = Material.tags.through.objects.using("sqlite").count()
    through_neon = Material.tags.through.objects.using("default").count()
    m2m_status = "MATCH" if through_sqlite == through_neon else "MISMATCH!"
    print(f"   • {'vault.Material.tags (M2M)':<35} SQLite: {through_sqlite:<4} | Neon: {through_neon:<4} [{m2m_status}]")

    print("\n" + "=" * 60)
    if all_matched and m2m_status == "MATCH":
        print("🎉  All data from SQLite successfully migrated to Neon PostgreSQL!")
    else:
        print("⚠️  Migration finished with discrepancies. Please check output above.")
    print("=" * 60)

if __name__ == "__main__":
    migrate_data()
