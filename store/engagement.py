from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from .models import AchievementAward, EngagementMetric, MissionActivity


MISSIONS = {
    'daily_views': {
        'title': 'Explore three skins',
        'description': 'Open three different skin listings today.',
        'action': 'view',
        'target': 3,
        'xp': 20,
        'period': 'daily',
    },
    'daily_battle': {
        'title': 'Vote in Skin Battle',
        'description': 'Choose your favorite in today’s comparison.',
        'action': 'battle',
        'target': 1,
        'xp': 15,
        'period': 'daily',
    },
    'daily_quiz': {
        'title': 'Skin knowledge check',
        'description': 'Answer today’s skin quiz correctly.',
        'action': 'quiz',
        'target': 1,
        'xp': 15,
        'period': 'daily',
    },
    'weekly_collection': {
        'title': 'Build a collection',
        'description': 'Create a collection this week.',
        'action': 'collection',
        'target': 1,
        'xp': 40,
        'period': 'weekly',
    },
}


def mission_period(period, today=None):
    today = today or timezone.localdate()
    return today - timedelta(days=today.weekday()) if period == 'weekly' else today


def record_mission_activity(user, action, object_key):
    for code, mission in MISSIONS.items():
        if mission['action'] != action:
            continue
        MissionActivity.objects.get_or_create(
            user=user,
            mission_code=code,
            period_start=mission_period(mission['period']),
            object_key=str(object_key)[:100],
        )


def record_metric(metric):
    today = timezone.localdate()
    EngagementMetric.objects.get_or_create(metric=metric, day=today)
    EngagementMetric.objects.filter(metric=metric, day=today).update(count=F('count') + 1)


def award_achievement(user, code, title):
    AchievementAward.objects.get_or_create(user=user, code=code, defaults={'title': title})


def claim_mission(user, code):
    mission = MISSIONS.get(code)
    if not mission:
        return False
    period = mission_period(mission['period'])
    progress = MissionActivity.objects.filter(
        user=user, mission_code=code, period_start=period
    ).count()
    if progress < mission['target']:
        return False
    try:
        with transaction.atomic():
            from .models import MissionClaim, UserProfile

            MissionClaim.objects.create(
                user=user,
                mission_code=code,
                period_start=period,
                experience_awarded=mission['xp'],
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.experience_points = F('experience_points') + mission['xp']
            profile.save(update_fields=['experience_points'])
    except IntegrityError:
        return False
    award_achievement(user, 'first_mission', 'First mission completed')
    if user.mission_claims.count() >= 5:
        award_achievement(user, 'mission_regular', 'Mission regular')
    return True
