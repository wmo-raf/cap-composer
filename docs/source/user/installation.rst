Installation
============

The WMO CAP Composer can be installed in two ways:

1. As a standalone complete Wagtail project
2. As a set of Wagtail apps that can be integrated into an existing Wagtail project, such as `ClimWeb <climweb.readthedocs.io>`_.

The following sections provide instructions on how to install the WMO CAP Composer as a standalone project using a docker-compose stack.

Standalone Installation
-----------------------

This option will set up a Wagtail project together with the complete components required to run the WMO CAP Composer.

1. **Clone the repository**

   .. code-block:: shell

      git clone https://github.com/World-Meteorological-Organization/cap_composer.git

2. **Change into the project directory**

   .. code-block:: shell

      cd cap_composer

3. **Create an initial .env file and required host data directories**

   .. code-block:: shell

      source create-initial-config.sh /home/$USER/cap_composer-data

4. **Replace localhost in the `.env` file to your server's IP address or domain name**

   .. code-block:: shell

      sed -i 's/localhost/<your_ip_or_domain>/g' .env

   Or use your favorite text editor to edit the .env file and update the `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` variables.

5. **Copy the nginx configuration file**

   .. code-block:: shell

      cp nginx/nginx.conf.sample nginx/nginx.conf

6. **Copy the docker-compose file**

   .. code-block:: shell

      cp docker-compose.sample.yml docker-compose.yml

7. **Build the Docker containers**

   .. code-block:: shell

      docker compose build

   This may take some time to download and build the required Docker images, depending on your internet connection.

8. **Run the Docker containers**

   .. code-block:: shell

      docker compose up -d

9. **Check the logs to ensure everything is running correctly**

   .. code-block:: shell

      docker compose logs -f

   In case of any errors, see the troubleshooting section below for some helpful
   tips: `Troubleshooting standalone installation`_

10. **Check the CAP Composer homepage at** ``http://<your_ip_or_domain>:8080``.

   You should see the following page:

   .. image:: ../_static/images/cap_composer_homepage.png
      :alt: WMO CAP Composer Homepage

12. **Create a superuser**

    .. code-block:: shell

       docker compose exec cap_composer cap_composer createsuperuser

13. **Login to the Wagtail admin**

   Visit ``http://<your_ip_or_domain>:8080/cap_composer/login`` and you should see the login-page:
    
   .. image:: ../_static/images/cap_composer_login.png
      :alt: CAP Composer Login Page 

   Login with the superuser credentials you created in the previous step.
   You should see the Wagtail admin page, along with the CAP Composer components:

   .. image:: ../_static/images/cap_composer_admin.png
      :alt: CAP Composer Wagtail Admin Dashboard

Your installation is now complete. 

You can now proceed with the configuration of the Wagtail site and the CAP Composer components, see :ref:`configuration`

Please note that you should not expose port 8080 of your host on the public internet. 

To make your CAP Composer available over the public internet, see :ref:`securing-your-installation`.