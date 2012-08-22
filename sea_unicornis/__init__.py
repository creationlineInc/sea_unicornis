from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('sea_unicornis')


def kotti_configure(settings):
    settings['kotti.includes'] = settings['kotti.includes'] \
        + ' sea_unicornis.events' \
        + ' sea_unicornis.views'
