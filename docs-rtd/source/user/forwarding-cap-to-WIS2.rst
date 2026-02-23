.. _cap-alerts:

Publishing CAP XML on WIS2
==========================

The `WMO Information System 2.0 (WIS 2.0) <https://community.wmo.int/en/activity-areas/wis/WIS2-overview>`_ is a new framework for data sharing between WMO Members, which went operational in 2025. 
In WIS2 data publisher operate a WIS2 node to publish WIS2 Notification Messages (WNM) containing data and metadata using an MQTT broker. 
Global Brokers subscribe to all registered WIS2 Nodes to republish the WIS2 Notifications Messages to enable global data sharing.

The CAP Composer can be configured to send data-notifications containing the CAP XML over MQTT to enable an event-based processing of CAP alerts.

*NOTE: the MQTT notifications sent by the CAP Composer are not WNM compliant messages but they contain the CAP XML as a payload for the receiving system to process the CAP alert.*

Publishing CAP Alerts to a WIS2box
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data providers having implemented a WIS2 Node using the `wis2box <https://docs.wis2box.wis.wmo.int/en/latest>`_ software, can perform the following steps to publish CAP Alerts on the WIS2 network:

1. **Create the corresponding dataset on the wis2box-instance**
2. **Configure MQTT Brokers on the CAP-composer-instance**

These steps are described in detail in the wis2box-documentation at: `Publishing CAP XML with wis2box <https://docs.wis2box.wis.wmo.int/en/latest/user/cap-alerts.html>`_.