import openai
from lib_common import load_settings


def extract_order_info(user_content: str):
    endpoint, key = load_settings("openai", "app_setting.yml")
    client = openai.AzureOpenAI(
        api_key=key,
        api_version="2023-05-15",
        azure_endpoint=endpoint
    )

    deployment_name = "gpt-4.1-mini"

    system_prompt = '''
以下の指示に従って情報を抽出し、指定されたJSON形式で返答してください。

# Steps
1. テキスト全体を読み取り、以下の情報を抽出します：
   - **顧客名**: 顧客の名前（必要であれば「様」や敬称を除外）。
   - **注文番号**: オーダーに関連する明確な番号。
   - **納期**: 配送予定日、または納品予定日を具体的に特定。
2. 情報が不足している場合は、空欄（`""`）で記載し返答してください。

# Output Format
以下のJSON形式で回答してください：
{
  "customer_name": "顧客名",
  "order_id": "注文番号",
  "delivery_date": "納期"
}

- 出力には不要な文字や敬称（例：「様」など）は含めないでください。

# Examples

## インプット:
```
こんにちは。以下のご注文の確認をお願いします。
注文番号は67890です。顧客名は佐藤 花子様、納期は12月15日を予定しております。
```

## アウトプット:
{
  "customer_name": "佐藤 花子",
  "order_id": "67890",
  "delivery_date": "12月15日"
}


# Notes
- 文字表記の揺れ：「納期」「配送予定日」などの言葉の違いに注意し、文意を正確に読み取り納期情報を取得してください。
- 件名や署名など、不要な部分は抽出対象に含めないようにしてください。
'''
    #system_prompt = "You are an AI assistant."

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    user_content = "株式会社テストの佐藤様より、注文番号 #X123 のご注文がありました。納期は7月25日とのことです。"
    extracted_info = extract_order_info(user_content)
    print(extracted_info)