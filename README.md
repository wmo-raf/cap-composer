# 🌍 Originated in WMO Africa, now a Global Open-Source Initiative

The WMO CAP Compposer is a [Wagtail](https://wagtail.io/)
based [Common Alerting Protocol](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html) (CAP) Warning
Composer developed by the World Meteorological Organization (WMO) Regional Office for Africa (RAF).

This is a web-based tool for creating and managing CAP alerts. It is designed to be used by National Meteorological and
Hydrological Services (NMHSs), disaster management agencies, and other organizations that have the authority to publish
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

## Documentation

Please consult the [WMO CAP Composer Documentation](https://cap-composer.readthedocs.io/en/latest/) for information on installing and using the CAP Composer.

## Legal Disclaimer

See [LEGAL.md](LEGAL.md)

## Credits 🎖️

The WMO CAP Composer was developed by the following [NORCAP](https://www.nrc.no/expert-deployment/norcap-what-we-do)-funded developers:

- [Grace Amondi](https://github.com/Grace-Amondi)
- [Erick Otenyo](https://github.com/erick-otenyo)