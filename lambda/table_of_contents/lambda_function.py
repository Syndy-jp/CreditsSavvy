import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def lambda_handler(event, context):
    data = event
    theme: str = data["theme"]
    #目次の作成(成功するまで10回トライ)
    trial = 1
    for i in range(trial):
        try:
            table_of_contents: str = generate_table_of_contents(theme)
            table_of_contents_json: dict = json.loads(table_of_contents)
            break
        except json.JSONDecodeError:
            # chatgptがjsonを返さない場合があるので、その場合は再度トライする
            if i == trial - 1:
                raise
            pass
    response_data: dict ={
                'table_of_contents': table_of_contents_json,
        }
    return {
        'statusCode': 200,
        'body': response_data,
    }

# 目次を生成
def generate_table_of_contents(theme: str) -> str:
    print("関数には入れた")
    prompt = f"""
    ##PURPOSE: "{theme}"の講義のラジオドラマを作成します。
    以下の制約に厳密に従って、"{theme}"のための目次（最大6つまで）を準備してください。
    出力は以下のようにしてください。
    ##CONSTRAINTS:
    #出力の文字列はJSON形式である必要があります。
    #空白文字は"---"に置き換えて出力してください。
    #出力には、目次以外のものを含めないでください。
    #出力は日本語である必要があります。
    #以下の例（相対性理論）をそのまま出力しないでください。'{theme}'のための目次を作成してください。

    ##INPUT EXAMPLE:
    相対性理論
    ##OUTPUT EXAMPLE:
    {{
    "1": "特殊相対性理論の基礎",
    "2": "光速不変の原理",
    "3": "相対性の原理",
    "4": "一般相対性理論の基礎",
    "5": "重力場の方程式",
    "6": "時空の歪みと重力の影響"
    }}
    """
    print(prompt)
    # 説明を出力する
    tbl_of_content_response = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
        stop=None,
        model="gpt-3.5-turbo",
    )
    print("生成までいけた")
    tbl_of_content = tbl_of_content_response.choices[0].message.content
    return tbl_of_content