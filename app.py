from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import requests
import json
import uvicorn
import os

# 环境变量传入
sk_key = os.environ.get('sk-key', 'skkey')

# 创建一个FastAPI实例
app = FastAPI()

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建一个HTTPBearer实例
security = HTTPBearer()

# Pydantic模型定义
class QADocs(BaseModel):
    query: Optional[str]
    documents: Optional[List[str]]

# 获取access_token的函数
def get_access_token():
    #补充取得clientid、clientsc代码

    
    # 替换以下API Key和Secret Key为实际的值
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={clientid}&client_secret={clientsc}"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

# 向解析服务器请求响应的函数
def rerank_query_documents(query: str, documents: List[str]) -> List[dict]:
    access_token = get_access_token()
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/reranker/bce_reranker_base?access_token=" + access_token
    
    payload = json.dumps({
        "query": query,
        "documents": documents
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = response.json()
    
    if "results" in response_data:
        return response_data["results"]
    else:
        return []

# FastAPI路由定义
@app.post('/v1/rerank')
async def handle_post_request(docs: QADocs, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != sk_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization code",
        )
    
    try:
        results = rerank_query_documents(docs.query, docs.documents)
        return {"results": results}
    except Exception as e:
        print(f"报错：\n{e}")
        return {"error": "重排出错"}

# 主函数，用于运行FastAPI应用
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=6006)

