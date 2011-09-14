from zope.interface import implements
from zope.component import queryUtility

from zope.component import getAdapters
from zope.interface import Interface, alsoProvides

from Products.Five import BrowserView
from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.permission import AddTopics, ChangeTopics


from upfrontsystems.portlets.savedsearches.interfaces import ISavedSearch
from upfrontsystems.portlets.savedsearches.browser.interfaces import ISaveSearch
from upfrontsystems.portlets.savedsearches.browser.interfaces import IShowAdapters

import logging

class SaveSearch(BrowserView):
    """
    Supporting class for search saving view.
    """
    implements(ISaveSearch)
    

    def __call__(self):
        # get the search string
        search = self.request.get('SearchableText', '')
        # nothing to search, nothing to do
        # TODO: We should log some portal error here.
        if not search: return

        # Get the member tool
        pmt = getToolByName(self.context, 'portal_membership')

        # Get the member home folder
        userid = pmt.getAuthenticatedMember().id
        if userid:
            homefolder = pmt.getHomeFolder(userid)
        else:
            # At this point there is nothing we can do, so we return.
            # TODO: We should log some portal error here.
            return

        # Check for and create the savedsearches folder if necessary.
        savedsearches = None
        id = 'savedsearches'
        if not id in homefolder.objectIds():
            homefolder.invokeFactory(
                'Folder', id=id, title='My saved searches')
            savedsearches = homefolder._getOb(id)
            savedsearches.manage_permission(
                AddTopics, ['Manager', 'Owner'], 1)
            savedsearches.manage_permission(
                ChangeTopics, ['Manager', 'Owner'], 1)
        else:
            savedsearches = homefolder._getOb(id)

        # Create smart folder to in the member folder
        id="Saved search for - %s" %search
        crit_field = 'SearchableText'
        crit_type = 'ATSimpleStringCriterion'
        currentsearch = None
        # we update the topic if it already exists
        if not id in savedsearches.objectIds():
            savedsearches.invokeFactory("Topic", id=id, title=id)
            currentsearch = savedsearches._getOb(id)
            # mark this instance in order to find it again in the portlets, etc.
            alsoProvides(currentsearch, ISavedSearch)

            # now we configure the topic
            currentsearch.setDescription("Results for search: %s" %search)
            # Sort results based on date
            currentsearch.setSortCriterion("created", reversed=False)
            # Filter results based on searchable text
            text_criterion = currentsearch.addCriterion(crit_field, crit_type)
            text_criterion.setValue(search)
            # Display as table
            currentsearch.setCustomView("True")        
            currentsearch.setCustomViewFields(
                ("Title", "Description", "created"))
        else:
            currentsearch = savedsearches._getOb(id)
            # first we delete the old one, look in:
            # Products.ATContentTypes.content.topic.py for the reasons;
            # especialy in addCriterion and deleteCriterion
            # TODO: Find a better way to update the current criteria.
            id = 'crit__%s_%s' % (crit_field, crit_type)
            currentsearch.deleteCriterion(id)
            text_criterion = currentsearch.addCriterion(crit_field, crit_type)
            text_criterion.setValue(search)
    

class ShowAdapters(BrowserView):
    """
    Supporting class for search saving view.
    """
    implements(IShowAdapters)
    
    def get_all_multiadapters(self, context, request, interface=Interface):
        adapters = getAdapters((self.context, self.request), provided=interface)
        struct = []
        while adapters:
            try:
                struct.append(adapters.next())
            except StopIteration:
                break
        struct.sort(lambda a,b: cmp(a[0], b[0]))
        return struct
