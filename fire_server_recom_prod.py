# -*- coding: utf-8
from core.pyspell import Dictionary
from database import storage
import json
import redis
import time
import core.ngram_cosine
import datetime

f = Dictionary(storage_type='redis',edit_distance_max=2,best_suggestions_only=False)
store = storage.storage(storage_type='redis')
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)   # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
r = redis.Redis(connection_pool=pool)

def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8')
epoch = datetime.datetime.utcfromtimestamp(0)
def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0

def update_model(brandname,brandnamech,brandnameen,businesstype,brandid,recordstatus,workflowstatus,dataspace='query_meta_dev:'):
    try:
        usename=safe_unicode(brandname)
        cnname=safe_unicode(brandnamech)
        enname=safe_unicode(brandnameen)
        yetai=safe_unicode(businesstype)
        brand_name=safe_unicode(brandname)
        brand_id=brandid
        id_=brand_id
    
        f.add_word(safe_unicode(brand_name))
        query_meta=dataspace+brand_name
        store.sadd(safe_unicode(query_meta).strip(),brand_id)
        if safe_unicode(cnname) !=u'null' and safe_unicode(cnname)!=safe_unicode(brand_name):
            f.add_word(safe_unicode(cnname))
            query_meta=dataspace+cnname
            store.sadd(safe_unicode(query_meta).strip(),brand_id)
        if safe_unicode(enname) !=u'null' and safe_unicode(enname)!=safe_unicode(brand_name) and safe_unicode(enname)!=safe_unicode(cnname):
            f.add_word(safe_unicode(enname))
            query_meta=dataspace+enname
            store.sadd(safe_unicode(query_meta).strip(),brand_id)

        last_insert=convert_dt_to_epoch(datetime.datetime.now())
        namedict={}
        namedict['usename']=usename
        namedict['cnname']=cnname
        namedict['enname']=enname
        namedict['yetai']=yetai
        namedict['insert_time']=last_insert
        namedict['workflowstatus']=workflowstatus
        namedict['recordstatus']=recordstatus
        #增加jsondumps 不然load时会出问题
        namedict_dumps=json.dumps(namedict)
        #name=repr(usename)+'u'+repr(cnname)+'c'+repr(enname)+'e'
        r.set(id_, namedict_dumps)
        return {'Success':True,'Message':'Model updates successfully','Error':[]}
    except:
        return {'Success':False,'Message':'Model updates error','Error':{"Brandid": brand_id, "Message":u"失败原因"}}

def recommend(brandname,brandid,dataspace='query_meta_dev:'):
    query_name=brandname
    P=dict()
    candidates = f.lookup(safe_unicode(query_name).lower(),return_distances=True)
        
    #result={}
    if candidates == None: 
        return jsonify({'success':True,'recommend':None})
    i=0
    #k去重
    chongfu={}
    recom_list=[]
    id_dup=[]
    for k,c in candidates:
        gram_distance=core.ngram_cosine.distance_cosine_measure(query_name,safe_unicode(k),gram_filter=False,n=2)
        if gram_distance>0.3:
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
        #add dataspace "query_meta"
        query_info=safe_unicode(dataspace+k.strip())
        
        for _id in store.smembers_index(query_info):
            recom_info={}
            metainfo=r.get(_id)
            meta_json=json.loads(metainfo)
            
            if u'recordstatus' not in meta_json.keys():
                continue
            if u'workflowstatus' not in meta_json.keys():
                continue
            Recordstatus=meta_json['recordstatus']
            Workflowstatus=meta_json['workflowstatus']
            if Recordstatus=='INACTIVE':
                continue
            if Workflowstatus=='REJECTED' or Workflowstatus=='INACTIVE':
                continue
            #print('Workflowstatus',Workflowstatus)
            if _id in id_dup:
                continue
            else:
                id_dup.append(_id)
            recom_info['brandid']=_id
            recom_info['distance']=gram_distance
            recom_list.append(recom_info)
        #info_dict['recom_id']=list(set(recom_id))
        #P['top%drecom'%i]=info_dict
        i+=1
    result=recom_list#json.dumps(P)
    if len(result)>0:
        return {'success':True,'recommend':result,'Message':'Succsess'}
    else:
        return {'false':True,'Message':'None Similarity result for recommendition'}


