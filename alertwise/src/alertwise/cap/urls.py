from django.urls import path

from .views import (
    AlertListFeed,
    cap_geojson,
    get_home_map_alerts,
    get_latest_active_alert,
    get_cap_xml,
    get_cap_feed_stylesheet,
    get_cap_alert_stylesheet
)

urlpatterns = [
    path("home-map-alerts/", get_home_map_alerts, name="home_map_alerts"),
    path("latest-active-alert/", get_latest_active_alert, name="latest_active_alert"),
    path("api/cap/rss.xml", AlertListFeed(), name="cap_alert_feed"),
    path("api/cap/alerts.geojson", cap_geojson, name="cap_alerts_geojson"),
    path("api/cap/<uuid:guid>.xml", get_cap_xml, name="cap_alert_xml"),
    path("cap-feed-style.xsl", get_cap_feed_stylesheet, name="cap_feed_stylesheet"),
    path("cap-alert-style.xsl", get_cap_alert_stylesheet, name="cap_alert_stylesheet"),
]
