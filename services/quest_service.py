from datetime import date
from services.supabase_client import supabase


def get_quest(thread_id: int):
    res = supabase.table("quests").select("*").eq("thread_id", str(thread_id)).execute()
    return res.data[0] if res.data else None


def save_quest(thread_id, channel_id, tag, points, images_required, reward_message):
    supabase.table("quests").upsert(
        {
            "thread_id": str(thread_id),
            "channel_id": str(channel_id),
            "tag": tag,
            "points": points,
            "images_required": images_required,
            "reward_message": reward_message,
        }
    ).execute()


def can_claim(discord_id, quest):
    if quest["tag"] == "obligatoire":
        res = (
            supabase.table("quest_claims")
            .select("id")
            .eq("discord_id", discord_id)
            .eq("thread_id", quest["thread_id"])
            .execute()
        )
        return not res.data

    if quest["tag"] == "journaliere":
        res = (
            supabase.table("quest_claims")
            .select("id")
            .eq("discord_id", discord_id)
            .eq("thread_id", quest["thread_id"])
            .gte("claimed_at", str(date.today()))
            .execute()
        )
        return not res.data

    return False


def award_points(discord_id, quest):
    supabase.table("quest_claims").insert(
        {
            "discord_id": discord_id,
            "thread_id": quest["thread_id"],
        }
    ).execute()

    supabase.rpc(
        "increment_points", {"p_discord_id": discord_id, "p_points": quest["points"]}
    ).execute()


def get_user_points(discord_id: str) -> int:
    res = (
        supabase.table("users")
        .select("points")
        .eq("discord_id", discord_id)
        .single()
        .execute()
    )

    if not res.data:
        return 0

    return res.data["points"]


def get_leaderboard(limit: int = 10):
    res = (
        supabase.table("users")
        .select("discord_id, points")
        .order("points", desc=True)
        .limit(limit)
        .execute()
    )

    return res.data or []
