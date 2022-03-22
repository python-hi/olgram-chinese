import gettext
from olgram.settings import BotSettings
from os.path import dirname

locales_dir = dirname(__file__)

lang = BotSettings.language()
if lang == "ru":
    _ = lambda x: x
else:
    t = gettext.translation("olgram", localedir=locales_dir, languages=[lang])
    _ = t.gettext
