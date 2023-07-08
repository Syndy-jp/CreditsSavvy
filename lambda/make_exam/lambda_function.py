import openai
import json
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

def lambda_handler(event, context):
    data: dict = event
    selections: int = data["selection"]
    descriptions: int = data["description"]
    script: str = data["script"]
    
    #試験問題の作成
    exam: dict = gen_exam(script, selections, descriptions)
    
    return {
        'statusCode': 200,
        'body': exam,
    }
    
    
def gen_exam(script: str, selection: int, description: int) -> dict:
    prompt = f"""
    ##PURPOSE: 以下の説明文について、{selection}個の選択肢問題と{description}個の記述問題が入ったjson形式の文字列を1つ作成してください。
    「{script}」
    ##CONSTRAINTS:
    #出力は以下の形式である必要があります。絶対に2つ以上の以下のjson形式の文字列を出力しないでください。
    {{
        "select" : [json形式で選択問題が{selection}個入っている配列],
        "descript" : [記述問題の文字列が{description}個入っている配列]
    }}
    #選択肢と解説以外の余分な回答はしないでください
    #以下が入出力の例ですが、囲碁の例でそのまま出力しないでください。上であげた説明文についてこれと同じ形式で出力してください。
    
    ##INPUT EXAMPLE:
    「
    囲碁は2人のプレイヤーが碁盤上で石を交互に置き、領域を確保するゲームです。碁盤は19×19の格子状になっており、石は黒と白の2色で表されます。石は交差点に配置され、一度置かれた石は移動することはありません。
    石を置くことで領域を囲み、相手の石を取ることが目的です。石同士が隣接すると連と呼ばれるグループが形成されます。連は縦横に隣接した同じ色の石の連続した集まりです。連を取られると、その連に含まれる石は取られます。
    ゲーム終了時には、碁盤上の石の数と領域の大きさを競います。石の数が多いほうが有利ですが、碁盤上の領域を確保することも重要です。領域は自分の石で囲まれた空白の交差点の数です。
    なお、一手で石を置いた後に、その石を取ることはできません。また、同じ局面が繰り返された場合や自殺手（自分の石を取る手）は禁止されています。
    囲碁は戦略性の高いゲームであり、碁盤上の地の利や石の配置、相手の石の攻略などを考慮しながらプレイします。
    」
    について2つの選択問題と2つの記述問題が含まれるjson形式の文字列を1つ作成してください。
    ##OUTPUT EXAMPLE:
    {{
        "selection": [
        {{
        "question": "囲碁の終了条件は？",
        "choices": ["石の数が多い方が勝ち", "領域の大きさが大きい方が勝ち", "相手の石を全て取った方が勝ち", "自分の石を全て配置した方が勝ち"],
        "answer": "石の数が多い方が勝ち",
        "explanation": "ゲーム終了時には、碁盤上の石の数と領域の大きさを競いますが、囲碁の終了条件は石の数が多い方が勝つことです。領域の大きさも重要ですが、石の数が決定的な要素となります。"
        }},
        {{
        "question": "囲碁で使用される石の色は？",
        "choices": ["赤と青", "黒と白", "緑と黄", "紫とオレンジ"],
        "answer": "黒と白",
        "explanation": "囲碁で使用される石は黒と白の2色です。黒の石と白の石が交互に碁盤上に配置されます。石の色でプレイヤーを区別することができます。"
        }}
        ],
        "description": [
        "囲碁で勝利する上で重要な点は何か？",
        "囲碁での地の利としてどのような要素があるか？"
        ]
    }}
    """
    response = openai.ChatCompletion.create(
        messages=[{"role": "system", "content": 'あなたは優秀な学者であり教師です'}, {"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
        stop=None,
        model="gpt-3.5-turbo",
    )
    
    return json.loads(response.choices[0].message.content)