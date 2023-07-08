import openai
import json
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

def lambda_handler(event, context):
    data: dict = event
    question: str = data["question"]
    answer: str = data["answer"]
    
    #講評の作成
    commentary: str = make_comment(question, answer)
    
    return {
        'statusCode': 200,
        'body': commentary,
    }

def make_comment(question: str, answer: str) -> str:
    prompt = f"""
    {question}という問題に対して、{answer}という解答をしました。
    この解答について、採点・講評をしてください。
    """
    response = openai.ChatCompletion.create(
        messages=[{"role" : "system", "content" : "あなたは優秀な大学講師です。"}, {"role": "user", "content": prompt}],
        max_tokens=1024,
        n=1,
        temperature=0.7,
        stop=None,
        model="gpt-3.5-turbo",
    )