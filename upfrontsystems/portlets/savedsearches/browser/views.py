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
    
    # upon receiving the search form we look here to see what criterion type
    # to use for which field.
    # field name first as key, matched to criterion.
    # you can look in Products.ATContentTypes.criteria/* for some more ideas.
    criteria_map = {'SearchableText': 'ATSimpleStringCriterion',
                    'Title'         : 'ATSimpleStringCriterion',
                    'Content'       : 'ATSimpleStringCriterion',
                    'Description'   : 'ATSimpleStringCriterion',
                    'portal_type'   : 'ATPortalTypeCriterion',
                    'Creator'       : 'ATSimpleStringCriterion',
                    'review_state'  : 'ATSelectionCriterion',
                    #'created'       : 'ATFriendlyDateCriteria',
                   }

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
            # get the correct folder, create it if it does not exist and
            # set the necessary permissioins.
            savedsearches = self.getSavedSearchesFolder(homefolder)

            id="Saved search for - %s" %search
            currentsearch = None
            # we update the topic if it already exists or we create it.
            if not id in savedsearches.objectIds():
                savedsearches.invokeFactory("Topic", id=id, title=id)
                currentsearch = savedsearches._getOb(id)

                # mark this instance in order to find it again in the portlets, etc.
                alsoProvides(currentsearch, ISavedSearch)

                # now we configure the topic
                currentsearch.setDescription("Results for search: %s" %search)
                # Sort results based on date
                currentsearch.setSortCriterion("created", reversed=False)
                # Display as table
                currentsearch.setCustomView("True")        
                currentsearch.setCustomViewFields(
                    ("Title", "Description", "created"))
            else:
                currentsearch = savedsearches._getOb(id)
                # first we delete the old criteria look in:
                # Products.ATContentTypes.content.topic.py for the reasons;
                # especialy in addCriterion and deleteCriterion
                self.cleanupCriteria(currentsearch)
            
            # now we add the required criteria
            self.addCriteria(currentsearch)
            # get on over to our new topic/ saved search

            msg = 'Search saved.'
            putil = getToolByName(self.context, 'plone_utils')
            putil.addPortalMessage(msg, 'info')
            url = currentsearch.absolute_url()
            return self.request.response.redirect(url)
        else:
            # At this point there is nothing we can do, so we return.
            # TODO: We should log some portal error here.
            return


    def addCriteria(self, currentsearch):
        for crit_field, crit_type in self.criteria_map.items():
            value = self.request.get(crit_field)
            if value:
                # date criteria have to be handled a little differently.
                if crit_type == 'ATFriendlyDateCriteria':
                    value = self.getDays(value)
                criterion = currentsearch.addCriterion(crit_field, crit_type)
                criterion.setValue(value)


    def cleanupCriteria(self, currentsearch):
        # TODO: Find a better way to update the current criteria.
        for criterion in currentsearch.listCriteria():
            id = criterion.getId()
            currentsearch.deleteCriterion(id)


    def getSavedSearchesFolder(self, homefolder):
        # Check for and create the savedsearches folder if necessary.
        id = 'savedsearches'
        savedsearches = None
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
        return savedsearches
    

    def getDays(self, date):
        return 1

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
