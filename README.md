模型更新：

```javascript
curl -d '{"brandname":"usename","brandnamech":"cnname","brandnameen":"enname","businesstype":"yetai","brandid":1001,"recordstatus":"ACTIVATE","workflowstatus":"ACTIVATE"}' -H "Authorization: Token dev_test" http://knowledge.wanda.cn:8088/update_model
```

Response:

{"Message": "Model updates successfully", "Success": true, "Error": []}







相似查询：

```javascript
curl -d '{"brandname": "龙城大牌档","brandid":100049531}' -H "Authorization: Token dev_test" http://knowledge.wanda.cn:8088/recommend
```

Response:

{"Message": "Succsess", "success": true, "recommend": [{"distance": 0.0, "brandid": "100049531"}, {"distance": 0.19999999999999984, "brandid": "1032324"}]}

