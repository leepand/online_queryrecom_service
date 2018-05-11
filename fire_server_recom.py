# -*- coding: utf-8
from core.pyspell import Dictionary
from database import storage
import json
import redis
import time
import core.ngram_cosine

def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8')
f = Dictionary(storage_type='redis',edit_distance_max=2,best_suggestions_only=False)
store = storage.storage(storage_type='redis')
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
r = redis.Redis(connection_pool=pool)

def update_model(usename,cnname,enname,yetai,brand_name,brand_id):
    usename=safe_unicode(usename)
    cnname=safe_unicode(cnname)
    enname=safe_unicode(enname)
    yetai=safe_unicode(yetai)
    brand_name=safe_unicode(brand_name)
    brand_id=brand_id
    id_=brand_id
    f.add_word(safe_unicode(brand_name))
    query_meta='query_meta:'+brand_name
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
    return {'success':True,'message':'Successfully activated the model\'s API.\nPlease restart your server for these changes to take effect.'}

def recommend(brand_name,):
    query_name=brand_name
    P=dict()
    candidates = f.lookup(safe_unicode(query_name).lower(),return_distances=True)
        
    result={}
    if candidates == None: 
        return jsonify({'success':True,'recommend':None})
    i=0
    #k去重
    chongfu={}
    for k,c in candidates:
        gram_distance=core.ngram_cosine.distance_cosine_measure(query_name,safe_unicode(k),gram_filter=False,n=2)
        if gram_distance>0.5:
            continue
        if safe_unicode(k).strip() in chongfu:
            continue
        else:
            chongfu[safe_unicode(k).strip()]='test'
        info_dict={}
        if c>0.9:
            continue
        info_dict['recom_brand']=k.strip()
        info_dict['recom_dist']=gram_distance
        query_info=safe_unicode('query_meta:'+k.strip())
        recom_id=[]
        for _id in store.smembers_index(query_info):
            recom_id.append(_id)
        info_dict['recom_id']=list(set(recom_id))
        P['top%drecom'%i]=info_dict
        i+=1
    result=json.dumps(P)
    return {'success':True,'recommend':result}


