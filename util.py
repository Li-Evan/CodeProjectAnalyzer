from flask import g, current_app
from openai import OpenAI
import random
from constant import *
import tiktoken

# 计算字符串的token数
def count_tokens(text, model="gpt-3.5-turbo"):
    # 加载与指定模型兼容的编码器
    encoding = tiktoken.encoding_for_model(model)
    # 计算字符串的 tokens 数量
    tokens = encoding.encode(text)
    return len(tokens)

def split_long_text(string_list, max_tokens=8000, model="gpt-3.5-turbo"):
    split_string_list = []
    temp_list = []

    # 批量处理字符串，每次处理32个
    for i in range(0, len(string_list), 16):
        batch = string_list[i:i + 16]
        temp_string = " ".join(temp_list + batch)  # 拼接当前批次的字符串
        current_token_count = count_tokens(temp_string, model)
        if current_token_count > max_tokens:
            # 如果拼接后的字符串token数超过最大限制，保存之前的结果并重新开始拼接
            split_string_list.append(temp_string)
            temp_list = batch  # 开始新的拼接
        else:
            # 如果未超过最大token限制，继续累积当前批次的字符串
            temp_list += batch

    # 处理最后一组字符串
    if temp_list:
        split_string_list.append(" ".join(temp_list))

    return split_string_list


def talk_gpt(text):
    # print(count_tokens(text))

    api_key = OPENAI_API
    api_base = OPENAI_BASE_URL

    client = OpenAI(api_key=api_key, base_url=api_base)

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        # stream: False,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content


def talk_zhipu(text):
    from zhipuai import ZhipuAI
    api_key = ZHIPU_API_LIST[0]
    client = ZhipuAI(api_key=api_key)  # 填写您自己的APIKey
    response = client.chat.completions.create(
        model=ZHIPU_MODEL,  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ],
    )
    return response.choices[0].message.content


def talk_claude(text):
    api_key = OPENAI_API
    api_base = OPENAI_BASE_URL

    client = OpenAI(api_key=api_key, base_url=api_base)

    completion = client.chat.completions.create(
        model=CLAUDE_MODEL,
        # stream: False,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content


def talk_llm(text, llm_name=LLM_NAME):
    if llm_name == "openai":
        return talk_gpt(text)
    elif llm_name == "zhipu":
        return talk_zhipu(text)
    elif llm_name == "claude":
        return talk_claude(text)
    return talk_gpt(text)




if __name__ == '__main__':
    prompt = ""
    answer = talk_claude(prompt)
    print(answer)