Creating the Alert Page
=======================

To use the CAP Composer, you need to create at least one CAP Alert page. This is the page within Wagtail that will display the CAP Alerts to the public.

To create a CAP Alert page, follow these steps:

Login to the Wagtail admin interface and click on the "Pages" section in the sidebar.

Click on the "Edit" button next to the "Home" page to open the page editor:

.. image:: ../_static/images/cap_composer_edit_home.png
      :alt: WMO CAP Composer Edit Home Page

In the page editor, click on the 3 dots and click "Add Child Page" button to create a new page under the Home page.

.. image:: ../_static/images/cap_composer_add_child_page.png
      :alt: WMO CAP Composer Add Child Page

Provide a page title and a CAP Alerts Heading for your CAP Alert page:

.. image:: ../_static/images/cap_composer_cap_alert_page_settings.png
      :alt: WMO CAP Composer CAP Alert Page Settings

Open the menu at the bottom of the page and select "Publish" to publish the page:

.. image:: ../_static/images/cap_composer_publish_page.png
      :alt: WMO CAP Composer Publish Page

**Next we need to configure the "sites" settings to make sure that the CAP Alert page we just created is set as the default page for our website.**

Go to the "Settings" section in the sidebar and click on "Sites":

.. image:: ../_static/images/cap_composer_sites.png
      :alt: WMO CAP Composer Sites

Then click on the "Edit" button next to the default site to open the site settings and configure as in the example below, replacing the "Host name" field with your own domain name:

.. image:: ../_static/images/cap_composer_editing_site_settings1.png
      :alt: WMO CAP Composer Sites Settings

Then replace the default Home page with the CAP Alert page you just created by selecting the sub-page,
make sure to enable the "Is default site" option and then click on "Save":

.. image:: ../_static/images/cap_composer_editing_site_settings2.png
      :alt: WMO CAP Composer Sites Settings

Go to your URL at `https://<your_domain_name>` and you will see the entry for the CAP Alert page you just created:

.. image:: ../_static/images/cap_composer_homepage_with_cap_alert_page.png
      :alt: WMO CAP Composer Homepage with CAP Alert Page

**Next**: Proceed to the :doc:`user management <user-management>` section to create the groups and users required for composing and approving alerts.

