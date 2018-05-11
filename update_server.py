# -*- coding: utf-8
"""
model process
"""
import flask_profiler
from flask import Flask, request
from flask import jsonify
import threading
import pandas as pd

ctx = threading.local()
ctx.request = None
import flask_profiler

from pyspell import Dictionary
from storage import storage
import json
import redis


app = Flask(__name__)
app.config["DEBUG"] = True

def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8') 

@app.route('/update', methods=['POST'])
def update_model():
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        inputdata=json.loads(json.dumps(request.json))
        print(inputdata)
        usename=safe_unicode(inputdata['usename'])
        cnname=safe_unicode(inputdata['cnname'])
        enname=safe_unicode(inputdata['enname'])
        yetai=safe_unicode(inputdata['yetai'])
        brand_name=safe_unicode(inputdata['brand_name'])
        brand_id=inputdata['brand_id']
        id_=brand_id
        f.add_word(safe_unicode(brand_name))
        #r.sadd(safe_unicode(brand_name),safe_unicode(brand_id))
        query_meta='query_meta:'+brand_name
        query_meta='query_meta:'+brand_name
        #print safe_unicode(query_meta),safe_unicode(brand_id)
        store.sadd(safe_unicode(query_meta).strip(),brand_id)
        namedict={}
        namedict['usename']=usename
        namedict['cnname']=cnname
        namedict['enname']=enname
        namedict['yetai']=yetai
        #增加jsondumps 不然load时会出问题
        namedict_dumps=json.dumps(namedict)
        #name=repr(usename)+'u'+repr(cnname)+'c'+repr(enname)+'e'
        r.set(id_, namedict_dumps)
        return jsonify({'success':True,'message':'Successfully activated the model\'s API.\nPlease restart your server for these changes to take effect.'})

    elif request.headers['Content-Type'] == 'application/octet-stream':
        ff = open('./binary', 'wb')
        ff.write(request.data)
        ff.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"
    
    
    

    
    
@app.route('/query', methods=['POST'])
def recommend():
    #model2=TreeModel()
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        inputdata=json.loads(json.dumps(request.json))
        query_name=inputdata['brand_name']
        P=dict()
        candidates = f.lookup(safe_unicode(query_name).lower(),return_distances=True)
        
        result={}
        if candidates == None: 
            return jsonify({'success':True,'recommend':None})
        i=0
        #k去重
        chongfu={}
        for k,c in candidates:
            if safe_unicode(k).strip() in chongfu:
                continue
            else:
                chongfu[safe_unicode(k).strip()]='test'
            info_dict={}
            if c>0.4:
                continue
            info_dict['recom_brand']=k.strip()
            info_dict['recom_dist']=c
            query_info=safe_unicode('query_meta:'+k.strip())
            recom_id=[]
            for _id in store.smembers_index(query_info):
                recom_id.append(_id)
                #if len(r.get(_id))>0:
                #    meta_info=json.loads(r.get(_id))
                #    yetai=meta_info['yetai']
                #    cnname=meta_info['cnname']
                #   usename=meta_info['usename']
                #   enname=meta_info['enname']
            info_dict['recom_id']=list(set(recom_id))
            P['top%drecom'%i]=info_dict
            i+=1
        result=json.dumps(P)
        return jsonify({'success':True,'recommend':result})

    elif request.headers['Content-Type'] == 'application/octet-stream':
        fd = open('./binary', 'wb')
        fd.write(request.data)
        fd.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"


app.config['flask_profiler']={"enabled": True,"storage": {"engine": "mongodb"},"basicAuth":{"enabled": True,"username": "leepand","password":"admin"},"ignore": ["^/static/.*"]}
flask_profiler.init_app(app)
if __name__ == '__main__':
    f = Dictionary(storage_type='redis',edit_distance_max=2,best_suggestions_only=False)
    store = storage(storage_type='redis')
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)

    app.run(host="127.0.0.1", port=5666)