# Multi-Language Support Documentation

This Temple Management System now supports multiple languages including English and Malayalam.

## How It Works

The application uses **Flask-Babel** for internationalization (i18n). All user-facing strings are wrapped in the `_()` function (gettext).

## Adding Translations

### 1. Mark Strings for Translation

In Python files:
```python
from flask_babel import gettext as _
message = _('Hello World')
```

In Jinja2 templates:
```html
<h1>{{ _('Hello World') }}</h1>
```

### 2. Extract Translatable Strings

To create a translation template:
```bash
pybabel extract -F babel.cfg -o app/translations/messages.pot .
```

### 3. Create Translation Files

Create translation files for new languages:
```bash
# For Malayalam
pybabel init -i app/translations/messages.pot -d app/translations -l ml

# For other languages
pybabel init -i app/translations/messages.pot -d app/translations -l <language_code>
```

### 4. Update Existing Translations

When new strings are added:
```bash
pybabel update -i app/translations/messages.pot -d app/translations
```

### 5. Compile Translations

After editing .po files, compile them to .mo files:
```bash
pybabel compile -d app/translations
```

## Translation Files Structure

```
app/translations/
├── en/
│   └── LC_MESSAGES/
│       ├── messages.po    (English translations)
│       └── messages.mo    (Compiled English)
└── ml/
    └── LC_MESSAGES/
        ├── messages.po    (Malayalam translations)
        └── messages.mo    (Compiled Malayalam)
```

## Supported Languages

- `en` - English
- `ml` - Malayalam

Add more languages by:
1. Creating new .po files
2. Adding the language code to `app.config['LANGUAGES']` in `app/__init__.py`
3. Providing language switcher UI

## Language Switching

Users can switch languages via:
- Language selector on login page
- Set `session['language']` in your code
- Browser language preferences (as fallback)

## Current Translated Strings

The following strings are currently translated:
- Page titles
- Form labels
- Button text
- Navigation items
- System messages
- Flash messages

See `app/translations/ml/LC_MESSAGES/messages.po` for Malayalam translations.

## Adding More Translations

1. Update strings in templates/Python code using `_()` function
2. Run: `pybabel extract -F babel.cfg -o app/translations/messages.pot .`
3. Update translations: `pybabel update -i app/translations/messages.pot -d app/translations`
4. Edit .po files with translations
5. Compile: `pybabel compile -d app/translations`

## Tools for Translation

- **Poedit** - GUI editor for .po files (https://poedit.net)
- **VS Code Extension** - "gettext" extension for .po file editing
- **Lokalize** - KDE translation tool

## Example .po File Entry

```
msgid "Welcome back, %(name)s!"
msgstr "നിങ്ങളെ സ്വാഗതം, %(name)s!"
```

The `%(name)s` is a placeholder that will be replaced with actual values.

---

**Note:** Don't forget to compile translations after editing .po files for changes to take effect!
