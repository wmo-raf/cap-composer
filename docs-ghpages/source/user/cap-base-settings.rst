CAP Base Settings
=================

These are common details that are repeated across the CAP Composer tool and are set only once per country.

You can configure these details by navigating to CAP Base Settings page in the Wagtail admin interface:

.. image:: ../_static/images/cap_composer_select_cap_base_settings.png
      :alt: WMO CAP Composer Base Settings

Sender Details
--------------

These include:

1. CAP Sender name - Name of the sending institution
2. CAP Sender email - Email of the sending institution
3. WMO Register of Alerting Authorities OID - Use the official OID assigned to your country in the `WMO register of alerting authorities <https://alertingauthority.wmo.int/authorities.php>`_.
4. Logo of the institution (optional)
5. Contact details - This is the contact details to be included in the CAP Alert.

.. image:: ../_static/images/cap_composer_sender_details.png
      :alt: WMO CAP Composer Sender Details



Hazard Types
--------------

Here the NMHSs input the different types of hazards they monitor. They can select the hazards from a WMO predefined list of hazards or create a new custom hazard/event type. Each hazard type can be associated with an Icon, a Category and an Event Code

.. image:: ../_static/images/cap_composer_hazard_types.png
      :alt: WMO CAP Composer Sender Details


Predefined Areas
----------------

Here you can create a list of common regions that are known to experience alerts. This will save you time so that you do not have to draw the same area each time for new alerts. 

 **NOTE:**
 While drawing a boundary, if the area falls out of the UN Boundaries set, a warning and button will appear to snap the area back to the UN Boundaries. Snapping boundaries back to the UN Boundary ensures that the CAP Alert is displayed on Severe Weather and Information Centre (SWIC) platform.

.. image:: ../_static/images/cap_composer_predefined_areas.png
      :alt: WMO CAP Composer Predefined Areas

Languages
-----------

To add one or more languages, the Language code such as es and Language name such as Spanish. This languages will be useful when creating multiple Alert Infos for a CAP Alert where one alert info corresponds to another one Alert info by its translated language.

.. image:: ../_static/images/cap_composer_languages.png
      :alt: WMO CAP Composer Languages


UN Boundary
--------------

This section allows you to upload a GeoJSON file of the UN Country Boundary. Setting this will enable the UN Country Boundary check in the alertdrawing tools.

.. image:: ../_static/images/cap_composer_un_boundaries.png
      :alt: WMO CAP Composer UN Boundaries

Other Settings
---------------

Here you can limit the number of CAP Alerts that can are displayed at the same time on the website, reducing it will help to improve performance.

.. image:: ../_static/images/cap_composer_other_settings.png
      :alt: WMO CAP Composer Other Settings

Remember to **SAVE** the changes after editing the settings.

**Next**: You can now optionally proceed to the :doc:`Setting Boundaries <setting-boundaries>` section to set up the boundaries that can be used when creating the alert area.

Or you can directly proceed to the :doc:`Creating and Issuing Alerts <creating-alerts>` section to learn how to start creating CAP Alerts using the CAP Composer.