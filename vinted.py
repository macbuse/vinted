#! /home/gregmcshane/anaconda3/bin/python3.6 

import re
import json
import requests


class Vinted():
    '''wrap a logged in session to vinted
       you have to enter a valid user name/password'''
    
    def __init__(self, creds={'login': 'ssss',
                             'password': 'xxxx'}):
        
        self.creds = creds
        self.sess = None #requests session
        
    def get_page(self, url, params={}):
        '''fetch a page using current session'''
        return self.sess.get(
            url,
            params=params,
            headers = dict(referer=url))

    def login(self):
        '''login to vinted using the credentials in creds'''

        self.sess = requests.session()
        login_url = 'https://www.vinted.fr/member/general/login?ref_url='
        tt = self.sess.get(login_url).content.decode('utf-8')
        pp = re.compile('name="csrf-token" content="(.*?)"')
        mm = pp.search(tt)

        payload = self.creds
        payload["authenticity_token"] =  mm.group(1)
        

        result = self.sess.post( 'https://www.vinted.fr/member/general/login.json',
                                       json=json.dumps(payload),
                                       headers=dict(referer=login_url)
                                      )
        return result

    def get_items4member(self, member_id='32359937'):
        '''get all the items for the member
        do not attempt to decode the json
        return user_info as json and items as list of json'''

        base_url = 'https://www.vinted.fr/api/v2/users/'

        r = self.get_page(base_url + '%s/'%member_id)
        member_info = r.json()['user']

        num_items = member_info['item_count']
        if num_items == 0:
            return member_info, []

        url = base_url + '%s/items'%member_id
        all_items = []

        for k in range(1, num_items//48 + 2):
            print('page', k)
            r = self.get_page(url, 
                              params={'page': k, 'per_page': 48})
            all_items.extend( r.json()['items'])

        return member_info, all_items

    def get_friends4member(self, member_id='20263980'):
        '''get all the friends for the member
        return a list of pairs (member_id, pseudo)'''

        r = self.get_page('https://www.vinted.fr/member/general/followers/' + member_id)
        px = re.compile('class="follow__name".*?(\d+).*?>(.*?)<')
        return list(set(px.findall(r.content.decode('utf-8'))) )

from vinted_creds import creds

session = Vinted(creds=creds)
print(session.login().content.decode('utf-8'))

print(session.get_friends4member())
