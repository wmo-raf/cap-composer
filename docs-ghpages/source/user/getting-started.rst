.. _getting-started:

Getting started
===============

The CAP Composer is a web-application based on `Wagtail <https://wagtail.io/>`_. 
Wagtail is an Open Source Content Management System (CMS) written in Python and built on the Django web framework.

The CAP Composer source code contains docker-compose files to help define the required services and dependencies to setup a standalone version of the CAP Composer.
The standalone version of the CAP Composer is a complete Wagtail project that includes the CAP Composer components. It will require a host with the necessary resources to run the docker-compose stack.

If you already have a Wagtail project and would like to integrate the CAP Composer components, you can install the CAP Composer as a set of Wagtail apps.

Host requirements for standalone CAP Composer
---------------------------------------------

The standalone CAP Composer host requires a minimum of 2 vCPUs with 8 GB Memory and 24GB of local storage.

The following software dependencies are required:

- Docker
- Docker Compose

The following ports are used by the docker compose stack and should not be used by other services on the host:

- 8000 (CAP Composer)
- 80 (CAP Composer web proxy)
- 81 (Nginx Proxy Manager)
- 443 (SSL)
- 5432 (Postgres)

If you want to use different ports, you can modify the docker-compose.yml file during the installation process.

To run the CAP Composer in a production environment the server should have a public IP address and a domain name. Only port 443 and 80 should be open to the public.
You will need to configure DNS to point to the IP address of your server, after which you can setup SSL using the Nginx Proxy Manager.


