# -*- coding: utf-8 -*-

import logging
from pprint import pprint, pformat

from requests import session
import facebook

class FBPost(object):
    def __init__(self, data):
        self.message = data['message']
        self.id = data['id']
        self.updated_time = data['updated_time']
        self.comments = None

class FBComment(object):
    def __init__(self, data, reply=False):
        self.message = data['message']
        self.author_id = data['from']['id']
        self.author = data['from']['name']
        self.id = data['id']
        self.reply = reply
        if not self.reply:
            self.comment_count = data['comment_count']
        self.replies = None

    def __repr__(self):
        return '<Comment %r: "%r" by "%r"> (reply: %r)' % (
            self.id, self.message, self.author, self.reply)

class FBHelper(facebook.GraphAPI):
    def __init__(self, parent):
        self.logger = logging.getLogger(__name__)
        self.parent = parent
        self.app = self.parent.app
        self.page_id = self.app.config['FB_PAGE_ID']
        super(FBHelper, self).__init__(
            access_token=self.app.config['FB_ACCESS_TOKEN'],
            version='2.11'
        )

    def extend_access_token(self, short):
        with session() as s:
            while True:
                try:
                    args = {
                        'grant_type': 'fb_exchange_token',
                        'client_id': self.app.config['FB_APP_ID'],
                        'client_secret': self.app.config['FB_APP_SECRET'],
                        'fb_exchange_token': short
                    }
                    token = s.get('https://graph.facebook.com/oauth/access_token', params=args)
                    break
                except:
                    continue
        return token

    def get_access_token(self):
        pass

    def get_posts(self, query):
        return self.get_message(query, single=False)

    def get_post(self, query, single=True):
        ret = []
        for msg in self.get_object(self.app.config['FB_GROUP_ID'] + '/feed')['data']:
            if query in msg.get('message', ''):
                post = FBPost(msg)
                post.comments = self.get_comments(post.id)
                if single:
                    return post
                ret.append(post)
        return ret

    def get_comments(self, post, cursor=None):
        ret = []

        if cursor:
            data = self.get_object(post + '/comments?fields=message,from,comment_count&after=' + cursor)
        else:
            data = self.get_object(post + '/comments?fields=message,from,comment_count')

        for comment in data['data']:
            c = FBComment(comment)
            c.replies = self.get_replies(c)
            ret.append(c)

        if data['paging'].get('next'):
            ret.extend(self.get_comments(post, data['paging']['cursors']['after']))
        return ret

    def get_replies(self, comment, cursor=None):
        ret = []
        if not comment.comment_count:
            return ret

        print 'Getting replies for', pformat(comment)
        if cursor:
            try:
                data = self.get_object(comment.id + '?fields=comments&after=' + cursor)
            except facebook.GraphAPIError:
                # TODO: handle error
                print 'ERROR!'
                return []
        else:
            try:
                data = self.get_object(comment.id + '?fields=comments')
            except facebook.GraphAPIError:
                # TODO: handle error
                # try with comment #
                # Getting replies for comment <Comment u'953776941451583': "u'i\xf9 c\xe0scu'" by "u'Mario C. Cavallaro'"> (reply: False)
                print 'ERROR!'
                return []

        ret = [FBComment(x, reply=True) for x in data['comments']['data']]
        if data['comments']['paging'].get('next'):
            ret.extend(self.get_replies(comment.id, data['comments']['paging']['cursors']['after']))
        return ret



### page parsing: /922452414584036/feed

# {
#     "message": "AGGIORNAMENTO 1: avete tempo fino alle 20,00 del 12/12 per partecipare a questa prova tecnica. Usate l'equivalente di cadere, non usate cascari, attummuliarisi o verbi simili, solo l'equivalente di cadere!",
#     "updated_time": "2017-12-12T18:56:14+0000",
#     "id": "922452414584036_953747388121205"
# },

### list comments: 922452414584036_953747388121205/comments?fields=message,from

# {
#   "data": [
#     {
#       "message": "Palermo: iu caru.",
#       "from": {
#         "name": "Salvatore Matteo Baiamonte",
#         "id": "10203731475803683"
#       },
#       "comment_count": 0,
#       "id": "953747451454532"
#     },
#     {
#       "message": "je cadu",
#       "from": {
#         "name": "William Scavuzzo",
#         "id": "1478064985576632"
#       },
#       "comment_count": 3,
#       "id": "953747561454521"
#     },
#     {
#       "message": "Iu cascu",
#       "from": {
#         "name": "Eleonora Bufalino",
#         "id": "10157054427169498"
#       },
#       "comment_count": 8,
#       "id": "953747628121181"
#     },

### subcomment 953747561454521?fields=comments

# {
#   "comments": {
#     "data": [
#       {
#         "created_time": "2017-12-11T22:30:19+0000",
#         "from": {
#           "name": "Salvatore Matteo Baiamonte",
#           "id": "10203731475803683"
#         },
#         "message": "Detto proprio je?",
#         "id": "953748308121113"
#       },
#       {
#         "created_time": "2017-12-11T22:56:30+0000",
#         "from": {
#           "name": "William Scavuzzo",
#           "id": "1478064985576632"
#         },
#         "message": "la lettere  'e' è molto chiusa",
#         "id": "953756258120318"
#       },
