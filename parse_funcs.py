from datetime import datetime, timedelta, timezone
import re

def parse_duration(duration_str):
    """
    Converts an ISO 8601 duration string (e.g., 'PT1H7M23S')
    into a human-readable 'hh:mm:ss' format with leading zeros.

    Examples:
        'PT1H7M23S' → '01:07:23'
        'PT5M'     → '00:05:00'
        'PT45S'    → '00:00:45'
        '' or None → '00:00:00'
    """

    # Return default if duration string is empty or None
    if not duration_str:
        return "00:00:00"

    # Regex pattern to extract hours, minutes, seconds from ISO 8601 duration
    pattern = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

    # Match the pattern against the input string
    match = pattern.fullmatch(duration_str)

    # If pattern doesn't match, return the original string as fallback
    if not match:
        return duration_str

    # Extract matched groups (may be None if not present)
    hours, minutes, seconds = match.groups()

    # Convert to integers, defaulting to 0 if missing
    h = int(hours) if hours else 0
    m = int(minutes) if minutes else 0
    s = int(seconds) if seconds else 0

    # Format as zero-padded hh:mm:ss string
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_utc_params_for_moscow_day(date_str):
    """
    Given a date string in 'YYYY-MM-DD' format (interpreted in Moscow time, UTC+3),
    returns a dictionary with 'start' and 'end' fields in UTC ISO 8601 format,
    suitable for querying a full day's data via Clockify API.

    Example:
        Input: '2025-07-12'
        Output:
            {
                'start': '2025-07-11T21:00:00Z',
                'end':   '2025-07-12T20:59:59Z'
            }
    """

    # Define Moscow timezone (UTC+3)
    moscow_tz = timezone(timedelta(hours=3))

    # Parse input date and assign Moscow timezone
    day_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=moscow_tz)

    # Calculate end of the day (23:59:59)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)

    # Convert start and end times to UTC and format as ISO 8601 strings
    start_utc = day_start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    end_utc = day_end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    return {"start": start_utc, "end": end_utc}