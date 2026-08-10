# Manage Translations

Locale configurations are set in `capcomposer/src/capcomposer/config/settings/base.py` file under the **LOCALE_PATHS** variable


1. Generate ***.po** translation files for locale folders listed in LOCALE_PATHS

```sh
capcomposer makemessages -l fr -l es -l ar -l am -l sw -l en -l pt
```

2. Translate ***.po** locales files listed in LOCALE_PATHS 

```sh
capcomposer translate_messages -l fr -l es -l ar -l am -l sw -l en -l pt -u
```

3. Build docs in target language (generate ***.mo** files)

```sh
capcomposer compilemessages
```


## CROWDIN UPLOAD LOCAL Translations

Crowdin configurations are set in crowdin.yml file

```sh
export CROWDIN_TOKEN=crowdin_token
```

```sh
crowdin upload translations \
  --token $CROWDIN_TOKEN \
  --project-id 672958 \
  --auto-approve-imported
```