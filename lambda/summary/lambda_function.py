import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def lambda_handler(event, context):
    try:
        data: bin = event.get('body', '{}')
else:
    return return {        
            'statusCode': 500,
            'body': "データを読み込めてない",
        }
    
    # data = json.loads(event)
    # mp3: bin = data['mp3']
    
    script: str = speech2text(data)
    summary: str = generate_summary(script)
    
    return {        
            'statusCode': 200,
            'body': summary,
        }
    
    
def speech2text(audio_data: bytes) -> str:
    response = openai.Transcription.create(
        audio=audio_data,
        model='whisper',
        language='en'
    )
    transcription = response['transcriptions'][0]['text']
    return transcription  

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
    
    summary = response.choices[0].message.content
    
    return summary