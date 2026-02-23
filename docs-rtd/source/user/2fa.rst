2-Factor Authentication
=======================

The CAP Composer includes the `wagtail-2fa Django App <https://github.com/labd/wagtail-2fa>`_ to support 2-Factor Authentication for logging into the Wagtail admin site.

To enable 2-Factor Authentication all Wagtail Admin users edit .env file and set the following variable:

.. code-block:: shell

   WAGTAIL_2FA_REQUIRED=True

After setting this variable, restart the docker containers:

.. code-block:: shell

   docker compose down
   docker compose up -d

Now when you try to login using the users created with the `createsuperuser` command you will be prompted to setup 2-Factor Authentication.

To enable or disable 2-Factor Authentication for a group, you can use the checkbox in the group permissions.