# Alertwise

A [Wagtail](https://wagtail.io/)
based [Common Alerting Protocol](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html) (CAP) Warning
Composer.

This is a web-based tool for creating and managing CAP alerts. It is designed to be used by National Meteorological and
Hydrological Services (NMHSs) ,disaster management agencies, and other organizations that have the authority to publish
and disseminate CAP alerts.

The **Common Alerting Protocol (CAP)** provides an open, non-proprietary digital message format for all types of alerts
and notifications.

This tool formats published warnings into the CAP XML that follows the structure of the schema provided
at http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html

## 🌟 Features

- Modern user-friendly composer that follows [CAP 1.2](http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html)
  standard. Built on top of the awesome [Wagtail CMS](https://wagtail.org)
- Preview a CAP alert as you edit. Save drafts for sharing with colleagues and collaborating
- Inbuilt CAP validation. The page will not save if you have not input the required data according to CAP standard
- User-friendly alert area map tool that allows multiple ways of constructing alert geographic areas, while keeping the
  interface simple
    - Upload and use your country/territory's administrative boundaries
    - Draw a polygon
    - Draw a circle
    - Selecting predefined areas that you create beforehand for common alert areas
- Inbuilt publishing workflow using Wagtail's powerful page model, with automated emails to composers and approvers
- Collaborate with team members using inbuilt comments (similar to how you could do in Word) with automated
  notifications. Request for changes and approvals
- Publish realtime notifications/messages to third party integrations using MQTT messaging protocol
- Predefine a list of hazards types monitored by your institution, with intuitive icons
  from [OCHA humanitarian icons](https://brand.unocha.org/d/xEPytAUjC3sH/icons#/humanitarian-icons)
- Extendable to add your custom logic and functionality. The package provides an `abstract` django model that can be
  inherited for customizations.

## 🛠️ Installation

Alertwise can be installed in two ways:

1. As a standalone complete Wagtail project
2. As a set of Wagtail apps that can be integrated into an existing Wagtail project

### Standalone Installation

This option will set up a Wagtail project together with the complete components required to run Alertwise. Use this when
you want to have Alertwise as a standalone project, and not a component in a bigger project.

1. **Clone the repository**

```shell
git clone https://github.com/wmo-raf/alertwise.git
```

2. **Change into the project directory**

```shell
cd alertwise
```

3. **Copy the sample environment file**

```shell
cp .env.standalone.sample .env
```

4. **Edit the `.env` file to set your environment variables.** See
   the [Standalone Environment Variables](#standalone-environment-variables)
   below for more information. Use your favourite text editor to edit the file. For example, using `nano`:

```shell
nano .env
```

5. **Copy the nginx configuration file**

```shell
cp nginx/nginx.conf.sample nginx/nginx.conf
```

6. **Copy the docker-compose file**

```shell
cp docker compose.sample.yml docker-compose.yml
```

7. **Build the Docker containers**

```shell
docker compose build
```

This may take some time to download and build the required Docker images, depending on your internet connection.

8. **Run the Docker containers**

```shell
docker compose up -d
```

9. **Check the logs to ensure everything is running correctly**

```shell
docker compose logs -f
```

In case of any errors, see the troubleshooting section below for some helpful
tips [Troubleshooting standalone installation](#troubleshooting-standalone-installation)

10. **Access the application at `http://<ip_or_doman>:<ALERTWISE_WEB_PROXY_PORT>`**. Replace `<ip_or_domain>` with the
    IP
    address or domain name of your server, and `<ALERTWISE_WEB_PROXY_PORT>` with the port set in the `.env` file or `80`
    if not set.

11. **Create a superuser to access the admin dashboard**

```shell
docker compose exec alertwise alertwise createsuperuser
```

`alertwise` is a shortcut command to `python manage.py` in the Docker container.

12. **Access the admin dashboard at `http://<ip_or_doman>:<ALERTWISE_WEB_PROXY_PORT>/<ADMIN_URL_PATH>`**. Replace
    `<ADMIN_URL_PATH>` with the path set in the `.env` file or `alertwise-admin` if not set.

#### Standalone Environment Variables

For a quick start, only 3 environment variables are required: `SECRET_KEY`, `DB_PASSWORD`, and `REDIS_PASSWORD`. The
rest are optional and can be configured as required.

| Variable                          | Description                                                                                                                                                                                                                      | Required | Default                                        | More Details                                                                                            |
|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| SECRET_KEY                        | A unique secret key for securing your Django application. It’s used for encryption and signing. Do not share this key!                                                                                                           | YES      |                                                |                                                                                                         |
| DB_PASSWORD                       | Password for Alertwise database                                                                                                                                                                                                  | YES      |                                                |                                                                                                         |
| DB_USER                           | Username for Alertwise database                                                                                                                                                                                                  | NO       | alertwise                                      |                                                                                                         |
| DB_NAME                           | Name of the Alertwise database                                                                                                                                                                                                   | NO       | alertwise                                      |                                                                                                         |
| REDIS_PASSWORD                    | Password for Alertwise Redis Server                                                                                                                                                                                              | YES      |                                                |                                                                                                         |
| GUNICORN_NUM_OF_WORKERS           | Number of workers for Gunicorn. Recommended value should be `(2 x $num_cores) + 1` . For example, if your server has `4 CPU Cores`, this value should be set to `9`, which is the result of `(2 x 4) + 1 = 9`                    | NO       | 4                                              |                                                                                                         |
| DEBUG                             | A boolean that turns on/off debug mode. Never deploy a site into production with DEBUG turned on                                                                                                                                 | NO       | False                                          |                                                                                                         |
| WAGTAIL_SITE_NAME                 | The human-readable name of your installation which welcomes users upon login to the Wagtail admin.                                                                                                                               | NO       | AlertWise                                      |                                                                                                         |
| ADMIN_URL_PATH                    | Custom URL path for the admin dashboard. Do not use admin or an easy to guess path. Should be one word and can include an hyphen. DO NOT include any slashes at the start or the end.                                            | NO       | alertwise-admin                                |                                                                                                         |
| TIME_ZONE                         | A string representing the time zone for this installation. See the list of time zones. Set this to your country timezone                                                                                                         | NO       | UTC                                            | [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)          |
| ALLOWED_HOSTS                     | A list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent HTTP Host header attacks, which are possible even under many seemingly-safe web server configuration | NO       | *                                              | [Django Allowed Hosts](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-ALLOWED_HOSTS)   |
| CSRF_TRUSTED_ORIGINS              | A list of trusted origins for unsafe requests (e.g. POST).                                                                                                                                                                       | NO       | []                                             | [Django CSRF_TRUSTED_ORIGINS](https://docs.djangoproject.com/en/dev/ref/settings/#csrf-trusted-origins) |
| DJANGO_ADMINS                     | A list of all the people who get alertwise error notifications, in format "Name <name@example.com>, Another Name <another@example.com>"                                                                                          | NO       |                                                |                                                                                                         |
| WAGTAILADMIN_BASE_URL             | This is the base URL used by the Wagtail admin site. It is typically used for generating URLs to include in notification emails.                                                                                                 | NO       |                                                |                                                                                                         |
| LANGUAGE_CODE                     | The language code for the system. Available codes are `en` for English, `fr` from French, `ar` for Arabic, `am` for Amharic, `es` for Spanish, `sw` for Swahili. Default is `en` if not set                                      | NO       | en                                             |                                                                                                         |
| CAP_CERT_PATH                     | 	Path to the CAP XML signing certificate                                                                                                                                                                                         | NO       |                                                |                                                                                                         |
| CAP_PRIVATE_KEY_PATH              | Path to the CAP XML signing private key                                                                                                                                                                                          | NO       |                                                |                                                                                                         |
| CAP_SIGNATURE_METHOD              | Method used for CAP XML signing                                                                                                                                                                                                  | NO       | ECDSA_SHA256                                   |                                                                                                         |
| ALERTWISE_WEB_PROXY_PORT          | External Docker port for the Alertwise Nginx web server                                                                                                                                                                          | NO       | 80                                             |                                                                                                         |
| EMAIL_SMTP                        | Enables SMTP for sending emails. If set to a non empty variable, configure the `EMAIL_SMTP_*` variables below                                                                                                                    | NO       |                                                |                                                                                                         |
| EMAIL_SMTP_HOST                   | SMTP server host for sending emails                                                                                                                                                                                              | NO       |                                                |                                                                                                         |
| EMAIL_SMTP_PORT                   | SMTP email port                                                                                                                                                                                                                  | NO       |                                                |                                                                                                         |
| EMAIL_SMTP_USE_TLS                | Enables TLS encryption for SMTP                                                                                                                                                                                                  | NO       |                                                |                                                                                                         |
| EMAIL_SMTP_USER                   | SMTP username                                                                                                                                                                                                                    | NO       |                                                |                                                                                                         |
| EMAIL_SMTP_PASSWORD               | SMTP password                                                                                                                                                                                                                    | NO       |                                                |                                                                                                         |
| DEFAULT_FROM_EMAIL                | Default email address used for sending emails                                                                                                                                                                                    | NO       |                                                |                                                                                                         |
| DB_VOLUME_PATH                    | Path to the mounted volume for the database                                                                                                                                                                                      | NO       | ./docker/volumes/db                            |                                                                                                         |
| BACKUP_VOLUME_PATH                | Path to the mounted volume for backups                                                                                                                                                                                           | NO       | ./docker/volumes/backup                        |                                                                                                         |
| STATIC_VOLUME_PATH                | Path to the mounted volume for static files                                                                                                                                                                                      | NO       | ./docker/volumes/static                        |                                                                                                         |
| MEDIA_VOLUME_PATH                 | Path to the mounted volume for media files                                                                                                                                                                                       | NO       | ./docker/volumes/media                         |                                                                                                         |
| ALERTWISE_ENABLE_OTEL             | Enables OpenTelemetry for monitoring and tracing                                                                                                                                                                                 | NO       |                                                |                                                                                                         |
| OTEL_EXPORTER_OTLP_ENDPOINT       | Endpoint for OpenTelemetry data export                                                                                                                                                                                           | NO       |                                                |                                                                                                         |
| OTEL_RESOURCE_ATTRIBUTES          | Attributes for OpenTelemetry resources                                                                                                                                                                                           | NO       |                                                |                                                                                                         |
| OTEL_TRACES_SAMPLER               | Sampling method for OpenTelemetry traces                                                                                                                                                                                         | NO       | traceidratio                                   |                                                                                                         |
| OTEL_TRACES_SAMPLER_ARG           | Specifies the sampling rate or configuration for the chosen sampler. The value depends on the sampler type defined in `OTEL_TRACES_SAMPLER`                                                                                      | NO       | 0.1                                            |                                                                                                         |
| OTEL_PER_MODULE_SAMPLER_OVERRIDES | Custom sampling rules for specific modules                                                                                                                                                                                       | NO       | opentelemetry.instrumentation.django=always_on |                                                                                                         |
| ALERTWISE_DEPLOYMENT_ENV          | Deployment environment (e.g., production, staging)                                                                                                                                                                               | NO       | production                                     |                                                                                                         |
| UID                               | User ID for the Docker container                                                                                                                                                                                                 | NO       | User ID for the Docker container               |                                                                                                         |U
| GID                               | Group ID for the Docker container                                                                                                                                                                                                | NO       | Group ID for the Docker container              |                                                                                                         |

#### Important Notes:

1. **Required Variables**: Ensure SECRET_KEY, DB_PASSWORD, and REDIS_PASSWORD are always set.
2. **Security**: Avoid using default values for sensitive variables like SECRET_KEY or ADMIN_URL_PATH.
3. **Debug Mode**: Never set DEBUG=True in production.
4. **Time Zone**: Set TIME_ZONE to your local time zone for accurate timestamps.
5. **SMTP**: Configure email settings if your app needs to send emails.

#### Troubleshooting standalone installation

1. **Docker containers not starting**: Check the logs for any errors. Run `docker compose logs -f` to see the logs.
2. **Docker compose file parsing errors**: Ensure the `docker-compose.yml` file is correctly formatted. Check for any
   syntax errors. Use `docker compose config` to validate the file. Some symbols like dollar signs `($)` or `@` might be
   the culprit in password variables, especially `DB_PASSWORD`. Check your password and other variables for any special
   characters that might be causing issues.
3. **Database volume permission errors**: Ensure the `DB_VOLUME_PATH` is correctly set and the user running the
   database container has the correct permissions to read and write to the volume path. The default user id and group
   for the db container is `1000:1000`. You can assign the correct permissions to the volume path by running:
   `sudo chown -R 1000:1000  ./docker/volumes/db`, or the custom path if changed.
4. **Static/media/backup volume permission errors**: The same as above, ensure the `STATIC_VOLUME_PATH`,
   `MEDIA_VOLUME_PATH`, and `BACKUP_VOLUME_PATH` are correctly set and the user running the alertwise containers has the
   correct permissions to read and write to these volume paths. This is the user set by the `UID` and `GID` environment.
   Set the correct permissions by running `sudo chown -R <UID>:<GID>  ./path/to/volume`, for all the volumes.

## Legal Disclaimer

See [LEGAL.md](LEGAL.md)