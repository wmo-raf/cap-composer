================
WMO CAP Composer
================

The WMO CAP Composer is a web-application based on `Wagtail <https://wagtail.io/>`_ to help National Meteorological and
Hydrological Services (NMHSs) create and managing alerts formatted using the `Common Alerting Protocol <https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html>`_ (CAP) 
as per **OASIS CAP standard version 1.2**.

The WMO CAP Composer provides a user-friendly interface to create CAP alerts that can be drafted, reviewed, and published as pages on the website. 
The WMO CAP Composer also hosts an RSS feed to enable the distribution of the CAP alerts to other systems.


Wagtail is an Open Source CMS written in Python and built on the Django web framework. 
By using Wagtail, the WMO CAP Composer can offer a user-friendly interface to create CAP alerts that can be drafted, reviewed, and published as pages on the website.

The WMO CAP Composer is developed and supported by the `World Meteorological Organization (WMO) <https://public.wmo.int/en>`_ and `NORCAP <https://www.nrc.no/norcap>`_, the Capacity Development Programme of the `Norwegian Refugee Council <https://www.nrc.no/>`_.

Content of this documentation
=============================

.. toctree::
   :maxdepth: 1
   :caption: Setup and configuration
   :name: toc-user

   user/getting-started
   user/installation
   user/securing-your-installation
   user/creating-alert-page
   user/user-management
   user/cap-base-settings
   user/setting-boundaries
   user/2fa
   
.. toctree::
   :maxdepth: 1
   :caption: Managing CAP Alerts
   :name: toc-create

   user/creating-alerts

.. toctree::
   :maxdepth: 1
   :caption: Dissemination
   :name: toc-diss
   
   user/cap-rss-feed
   user/forwarding-cap-to-WIS2

Maintenance and support
=======================

The WMO CAP Composer source code is available on `GitHub <https://github.com/World-Meteorological-Organization/cap-composer>`_, which is a fork of `WMO-RAF/NORCAP version of the CAP Composer <https://github.com/wmo-raf/cap-composer>`_ that is developed as part of the ClimWeb project.

The support team of the WMO Secretariat is responsible for syncing the fork with the upstream repository, update the documentation and ensure the standalone version of the CAP Composer is working as expected.

Contributing
============

It is recommended that contributions for bug fixes, enhancements are made upstream in the `WMO-RAF/NORCAP version of the CAP Composer <https://github.com/wmo-raf/cap-composer>`_. The support team at WMO Secretariat will then sync the changes to the WMO CAP Composer repository and update the documentation accordingly.

To report any bugs or issues you encounter please use the `GitHub Issues <https://github.com/wmo-raf/cap-composer/issues>`_ page of the WMO-RAF/NORCAP CAP Composer repository.
