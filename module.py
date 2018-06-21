import requests, re
import sqlite3
import json
from BeautifulSoup import BeautifulSoup
import os
class JubeatParser:
	urls={}
	urls['license_song_list'] = 'http://p.eagate.573.jp/game/jubeat/qubell/p/information/music_list1.html?page=%d'
	urls['original_song_list'] = 'http://p.eagate.573.jp/game/jubeat/qubell/p/information/music_list2.html?page=%d'
	urls['info_api'] = 'https://qubellinfo.com/%s/api'
	settings={}
	settings['license_page'] = 2
	settings['original_page'] = 3
        def dbInit(self):
                init_query = 'create table if not exists songs(unique_id int not null primary key, title varchar(128), artist varchar(128), basic int not null, advanced int not null, extreme int not null)'
                init_query2 = 'create table if not exists logs(uid text not null primary key, refresh_date int not null, hash text not null)'
                init_query3 = 'create table if not exists difficulty(unique_id int not null primary key, diff_x int not null, diff_y int not null)'
                self.cursor.execute(init_query)
		self.cursor.execute(init_query2)
                self.cursor.execute(init_query3)
	def __init__(self,useDB=True):
		self.sess = requests.session()
		self.sessid = ""
		self.isLogined = False  
                if(useDB):
        		self.conn = sqlite3.connect("db")
        		self.cursor = self.conn.cursor()
    	        	self.dbInit()
	def getMusicList(self):
		ret=[]
		#license
		for i in xrange(1, self.settings['license_page']+1):
			resp = self.sess.get(self.urls['license_song_list']%i)
			resp.encoding='shift_jisx0213'
			s = BeautifulSoup(resp.text)
			songs = s.findAll('li',attrs={'class':'type0'})
			for song in songs:
				song_wrap={}
				unique_id = song.find('img')['src']
				unique_id = re.search(r'(\d+)\.gif',unique_id)
				song_wrap['unique_id'] = unique_id.group(0)[:-4]
				song_wrap['title'] = song.find('div',{'class':'name'}).find('span').text
				song_wrap['artist'] = song.find('div',{'class':'name'}).text[len(song_wrap['title']):]
				level = song.find('div',attrs={'class':'level'}).text[3:].split('/')
				song_wrap['basic'] = level[0]
				song_wrap['advanced'] = level[1]
				song_wrap['extreme'] = level[2]
				ret.append(song_wrap)
		for i in xrange(1, self.settings['original_page'] + 1):
                        resp = self.sess.get(self.urls['original_song_list']%i)
                        resp.encoding='shift_jisx0213'
                        s = BeautifulSoup(resp.text)
                        songs = s.findAll('li',attrs={'class':'type0'})
                        for song in songs:
                                song_wrap={}
                                unique_id = song.find('img')['src']
                                unique_id = re.search(r'(\d+)\.gif',unique_id)
                                song_wrap['unique_id'] = unique_id.group(0)[:-4]
                                song_wrap['title'] = song.find('div',{'class':'name'}).find('span').text
                                song_wrap['artist'] = song.find('div',{'class':'name'}).text[len(song_wrap['title']):]
                                level = song.find('div',attrs={'class':'level'}).text[3:].split('/')
                                song_wrap['basic'] = level[0]
                                song_wrap['advanced'] = level[1]
                                song_wrap['extreme'] = level[2]
                                ret.append(song_wrap)
		return ret
        def getSongImage(self, unique_id):
                key = unique_id[0]
                url = 'http://p.eagate.573.jp/game/jubeat/qubell/common/images/jacket/%s/id%s.gif' % (key, unique_id)
                req = self.sess.get(url, stream=True)
                if req.status_code == 200:
                        req.raw.decode_content = True
                        buf = req.content
                        if os.path.isfile('jackets/%s.gif'%(unique_id)) is False:
                                with open('jackets/%s.gif'%(unique_id),'wb') as f:
                                        f.write(buf)
	def insertSongToDB(self, arg):
		query = 'insert or replace into songs(unique_id, title, artist, basic, advanced, extreme) values(?,?,?,?,?,?)'
		for data in arg:
			self.cursor.execute(query, (data['unique_id'], data['title'], data['artist'], data['basic'], data['advanced'], data['extreme']))
		self.conn.commit()
	def getData(self, userid):
		resp = self.sess.get(self.urls['info_api']%userid)
		data = json.loads(resp.text)
		return data
        def toImage(self, uid, level=10, target='EXC'):
                data = self.getData(uid)
                if data['result'] is None:
                        return None
                query = "select * from songs where extreme=10"
                self.cursor.execute(query)
                song_list = self.cursor.fetchall()
                for song in song_list:
                        print song[0]
