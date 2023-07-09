import os
import json
import boto3
from contextlib import closing
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
BUCKET_NAME: str = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    data = json.loads(event.get('body', '{}'))
    theme: str = data['theme']
    table_of_contents:dict = data['table_of_contents']
    content:str = data['content']
    
    #キーポイントとスクリプトの作成
    trial: int = 3 #最大試行回数
    key_points:str
    script:str
    for i in range(trial):
        try:
            key_points, script = generate_explanation(theme, table_of_contents, content)
            key_points_json: dict = json.loads(key_points)
            break
        except json.JSONDecodeError:
            # chatgptがjsonを返さない場合があるので、その場合は再度トライする
            if i == trial - 1:
                raise
            pass
        
    #音声の生成
    audio_data:bytes = generate_audio(script)
    
    #s3へのアップロード
    url: str
    url = s3_upload(audio_data, theme, content)
    
    response_data: dict = {
        'script' : script,
        'key_points': key_points_json,
        'url': url,
    }
    return {        
            'statusCode': 200,
            'body': response_data,
        }
    
# 説明を生成
def generate_explanation(theme: str, table_of_contents: str, content: str) -> tuple[str, str]:
    prompt = f"""
    ##PURPOSE:
    ##目的: 現在、"{theme}"について以下のような構成で講義を進めています。
    {table_of_contents}
    今回は、"{content}"についての講義をお願いします。
    3~5つのキーポイントとスクリプトを用意してください。以下の制約を厳密に守る必要があります。
    ##CONSTRAINTS:
    ##出力は以下の形式である必要があります。
    キーポイント(json形式の文字列) @@@ スクリプト(文字列)
    #キーポイントとスクリプト以外の余分な回答はしないでください
    #話者は1人です
    #以下が入出力の例ですが、囲碁の例でそのまま出力しないでください。"{theme}"についてこれと同じ形式で出力してください。
    
    ##INPUT EXAMPLE:
    "囲碁"の以下の目次の中から
    {{
    "1": "囲碁の基本ルール",
    "2": "石の配置と石の動かし方",
    "3": "戦術と戦略",
    "4": "オープニングの基本",
    "5": "ミドルゲームの戦術",
    "6": "エンドゲームのテクニック"
    }}
    "囲碁の基本ルール"について教えてください。
    ##OUTPUT EXAMPLE:
    {{
    "1": "囲碁は2人のプレイヤーが碁盤上で石を交互に置き、領域を確保するゲームです。",
    "2": "石は黒と白の2色で表され、交差点に配置されます。",
    "3": "石を置くことで領域を囲み、相手の石を取ることが目的です。",
    "4": "石同士が接することで連と呼ばれるグループが形成され、連を取られると石は取られます。",
    "5": "ゲーム終了時に石の数と碁盤上の領域の大きさを競います。"
    }}
    @@@囲碁は2人のプレイヤーが碁盤上で石を交互に置き、領域を確保するゲームです。碁盤は19×19の格子状になっており、石は黒と白の2色で表されます。石は交差点に配置され、一度置かれた石は移動することはありません。石を置くことで領域を囲み、相手の石を取ることが目的です。石同士が隣接すると連と呼ばれるグループが形成されます。連は縦横に隣接した同じ色の石の連続した集まりです。連を取られると、その連に含まれる石は取られます。ゲーム終了時には、碁盤上の石の数と領域の大きさを競います。石の数が多いほうが有利ですが、碁盤上の領域を確保することも重要です。領域は自分の石で囲まれた空白の交差点の数です。なお、一手で石を置いた後に、その石を取ることはできません。また、同じ局面が繰り返された場合や自殺手（自分の石を取る手）は禁止されています。囲碁は戦略性の高いゲームであり、碁盤上の地の利や石の配置、相手の石の攻略などを考慮しながらプレイします。
    """
    
    # 説明を出力する
    sum_response = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
        stop=None,
        model="gpt-3.5-turbo",
    )

    sum: str = sum_response.choices[0].message.content
    print(sum)
    sum_list: list[str] = sum.split("@@@")
    key_points: str = sum_list[0]
    script: str = sum_list[1]
    return key_points, script

#音声を生成
def generate_audio(script: str) -> bytes:
    # スクリプトを読み込む
    session = boto3.Session(region_name="ap-northeast-1")
    polly = session.client("polly")

    response = polly.synthesize_speech(
        Text=script,
        Engine="neural",
        OutputFormat="mp3",
        VoiceId="Takumi")
    
    with closing(response["AudioStream"]) as stream:
      data = stream.read()
    
    return data
    
def s3_upload(audio: bytes, theme: str, content: str) -> str:
    # Boto3の初期化
    session = boto3.Session()
    s3 = session.client('s3')

    # S3バケット名とファイル名
    bucket_name = BUCKET_NAME
    object_key = f'{theme}/{content}.mp3'

    # バイトコードをS3にアップロード
    s3.put_object(
        Body=audio,
        Bucket=bucket_name,
        Key=object_key,
        ContentType='audio/mp3'  # コンテンツタイプを指定
    )

    presigned_url:str = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key
        },
        ExpiresIn=7200  # プリサインドURLの有効期限（秒）
    )
    return presigned_url, object_key