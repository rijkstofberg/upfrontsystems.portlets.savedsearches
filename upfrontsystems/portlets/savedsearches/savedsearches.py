from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# TODO: If you define any fields for the portlet configuration schema below
# do not forget to uncomment the following import
#from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from upfrontsystems.portlets.savedsearches.interfaces import ISavedSearch

# TODO: If you require i18n translation for any of your schema fields below,
# uncomment the following to import your package MessageFactory
#from upfrontsystems.portlets.savedsearches import SavedSearchesMessageFactory as _


class ISavedSearches(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISavedSearches)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Saved Searches"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('savedsearches.pt')

    def getSavedSearches(self):
        searches = {}

        pmt = getToolByName(self.context, 'portal_membership')
        # Get the member home folder
        userid = pmt.getAuthenticatedMember().id
        pc = getToolByName(self.context, 'portal_catalog')
        if userid:
            homefolder = pmt.getHomeFolder(userid)
            # at first login the home folder does not exist yet.
            if not homefolder: return {}
            
            if 'savedsearches' in homefolder.objectIds():
                brains = pc(object_provides=ISavedSearch.__identifier__,
                            path='/'.join(homefolder.getPhysicalPath()))
                searches['My searches'] = brains
            # get all searches shared with the current user
            brains = pc(object_provides=ISavedSearch.__identifier__)
            brains = [b for b in brains if b.Creator != userid]
            if brains: searches['Shared searches'] = brains
        return searches


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISavedSearches)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISavedSearches)
