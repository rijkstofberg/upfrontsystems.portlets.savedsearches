from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Saved Searches" theme, this interface must be its layer
       (in savedsearches/viewlets/configure.zcml).
    """

class ISaveSearch(Interface):
    """Helps us save the current search.
    """

class IShowAdapters(Interface):
    """Marker interface for a component that shows all adapters
       for a given context.
    """
