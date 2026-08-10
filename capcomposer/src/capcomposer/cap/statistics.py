import csv
import io
from collections import defaultdict

from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.translation import gettext as _


SEVERITY_ORDER = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
URGENCY_ORDER = ["Immediate", "Expected", "Future", "Past", "Unknown"]
CERTAINTY_ORDER = ["Observed", "Likely", "Possible", "Unlikely", "Unknown"]

SEVERITY_COLORS = {
    "Extreme": "#d42d41",
    "Severe": "#f08c11",
    "Moderate": "#f4cf00",
    "Minor": "#399cc7",
    "Unknown": "#82a8df",
}

STATUS_COLORS = {
    "Actual": "#2563EB",
    "Test": "#7C3AED",
    "Exercise": "#059669",
    "Draft": "#6B7280",
    "System": "#9CA3AF",
}


def _get_filtered_queryset(request_or_params):
    """
    Build a CapAlertPage queryset applying date-range and severity filters.
    Accepts either a Django request or a plain dict of params.
    """
    from django.db.models import Q
    from .models import CapAlertPage

    if hasattr(request_or_params, 'GET'):
        params = request_or_params.GET
    else:
        params = request_or_params

    qs = CapAlertPage.objects.all()

    start_date = params.get("start_date")
    end_date = params.get("end_date")
    severities = params.getlist("severity") if hasattr(params, 'getlist') else params.get("severity", [])

    if start_date:
        try:
            qs = qs.filter(sent__date__gte=start_date)
        except Exception:
            pass

    if end_date:
        try:
            qs = qs.filter(sent__date__lte=end_date)
        except Exception:
            pass

    if severities:
        # Severity lives in the first info block of the StreamField (JSONB).
        severity_q = Q()
        for s in severities:
            severity_q |= Q(info__0__value__severity=s)
        qs = qs.filter(severity_q)

    return qs


def get_alert_statistics(queryset):
    """
    Compute total count and all breakdowns from a CapAlertPage queryset.
    """
    total = queryset.count()

    # ── DB-level aggregations ───────────────────────────────────────────────
    by_status = {
        row["status"]: row["count"]
        for row in queryset.values("status").annotate(count=Count("id"))
    }

    by_msg_type = {
        row["msgType"]: row["count"]
        for row in queryset.values("msgType").annotate(count=Count("id"))
    }

    by_scope = {
        row["scope"]: row["count"]
        for row in queryset.values("scope").annotate(count=Count("id"))
    }

    by_sender = {
        row["sender"] or _("Unknown"): row["count"]
        for row in queryset.values("sender")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    }

    monthly_trend = [
        {
            "month": row["month"].strftime("%Y-%m") if row["month"] else "",
            "label": row["month"].strftime("%b %Y") if row["month"] else "",
            "count": row["count"],
        }
        for row in (
            queryset.annotate(month=TruncMonth("sent"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        if row["month"]
    ]

    # ── StreamField aggregations (iterate in Python) ────────────────────────
    by_severity = defaultdict(int)
    by_urgency = defaultdict(int)
    by_certainty = defaultdict(int)
    by_event = defaultdict(int)

    for alert in queryset.only("info"):
        for info_block in alert.info:
            if info_block.block_type == "alert_info":
                val = info_block.value
                by_severity[val.get("severity") or "Unknown"] += 1
                by_urgency[val.get("urgency") or "Unknown"] += 1
                by_certainty[val.get("certainty") or "Unknown"] += 1
                by_event[str(val.get("event") or _("Unknown"))] += 1
                break

    by_severity_ordered = {k: by_severity[k] for k in SEVERITY_ORDER if k in by_severity}
    by_urgency_ordered = {k: by_urgency[k] for k in URGENCY_ORDER if k in by_urgency}
    by_certainty_ordered = {k: by_certainty[k] for k in CERTAINTY_ORDER if k in by_certainty}
    by_event_top = dict(sorted(by_event.items(), key=lambda x: x[1], reverse=True)[:15])

    return {
        "total": total,
        "by_status": by_status,
        "by_msg_type": by_msg_type,
        "by_scope": by_scope,
        "by_sender": by_sender,
        "monthly_trend": monthly_trend,
        "by_severity": by_severity_ordered,
        "by_urgency": by_urgency_ordered,
        "by_certainty": by_certainty_ordered,
        "by_event": by_event_top,
        "severity_colors": {k: SEVERITY_COLORS.get(k, "#ccc") for k in by_severity_ordered},
        "status_colors": {k: STATUS_COLORS.get(k, "#ccc") for k in by_status},
    }


def export_alerts_csv(queryset):
    """
    Return a (str) CSV content for the given CapAlertPage queryset.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Title", "Sent", "Status", "Message Type", "Scope", "Sender",
        "Severity", "Urgency", "Certainty", "Event", "Area Description",
    ])

    for alert in queryset.order_by("-sent"):
        severity = urgency = certainty = event = area_desc = ""

        if alert.info:
            first_info = alert.info[0]
            if first_info.block_type == "alert_info":
                val = first_info.value
                severity = val.get("severity") or ""
                urgency = val.get("urgency") or ""
                certainty = val.get("certainty") or ""
                event = str(val.get("event") or "")

                areas = val.get("area") or []
                area_descs = []
                for area in areas:
                    area_val = getattr(area, "value", area) if hasattr(area, "value") else area
                    desc = None
                    if hasattr(area_val, "get"):
                        desc = area_val.get("areaDesc")
                    if desc:
                        area_descs.append(str(desc))
                area_desc = "; ".join(area_descs)

        writer.writerow([
            alert.pk,
            alert.title,
            alert.sent.strftime("%Y-%m-%d %H:%M") if alert.sent else "",
            alert.status,
            alert.msgType,
            alert.scope,
            alert.sender,
            severity,
            urgency,
            certainty,
            event,
            area_desc,
        ])

    return output.getvalue()
