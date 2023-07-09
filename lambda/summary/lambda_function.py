import os
import json
import boto3
from contextlib import closing
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
BUCKET_NAME: str = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    data = json.loads(event.get('body', '{}'))
    theme: str = data['script']
    
    #キーポイントとスクリプトの作成
    trial: int = 3 #最大試行回数
    key_points:str
    script:str
    for i in range(trial):
        try:
            summary = generate_summary(summary)
            break
        except json.JSONDecodeError:
            # chatgptがjsonを返さない場合があるので、その場合は再度トライする
            if i == trial - 1:
                raise
            pass
    
    response_data: dict = {
        'summary' : summary
    }
    return {        
            'statusCode': 200,
            'body': response_data,
        }
    
# 説明を生成
def generate_summary(script: str) -> str:
    prompt = f"""
    ##PURPOSE: 以下の説明文について、要約を生成してください。
    「{script}」
     ##CONSTRAINTS: 
     #要約文以外の余分な回答はしないでください
    """
    
    # 説明を出力する
    response = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
        stop=None,
        model="gpt-3.5-turbo",
    )
    
    return response.choices[0].message.content