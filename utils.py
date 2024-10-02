from datetime import datetime, timezone

def format_date_relative(dt: datetime):
    diff = datetime.now(timezone.utc) - dt

    days = diff.days
    weeks = int(days // 7)
    years = int(days // 365)
    hours = int(diff.total_seconds() // (60 * 60))
    minutes = int(diff.total_seconds() // 60)

    if years > 0:
        return f"{years} {"vuosi" if years == 1 else "vuotta"} sitten"
    
    if weeks > 0:
        return f"{weeks} {"viikko" if weeks == 1 else "viikkoa"} sitten"

    if days > 0:
        return f"{days} {"päivä" if days == 1 else "päivää"} sitten"
    
    if hours > 0:
        return f"{hours} {"tunti" if hours == 1 else "tuntia"} sitten"
    
    if minutes > 0:
        return f"{minutes} {"minuutti" if minutes == 1 else "minuuttia"} sitten"

    return "Nyt"
