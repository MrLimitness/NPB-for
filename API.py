import openai
import time
import re
import os
import subprocess
base_dir = "D:\\New_NPB"

openai.base_url = 'https://api.siliconflow.cn/v1/'
openai.api_key = 'sk-lxmpctywfxndtshonqgixypnockmmtaaqcfzcxilysircimv'

def ask_gpt_question(prompt, max_retries=5, retry_delay=5):
    """
    最简单的API调用, print(ask_gpt_question("hello")
    """
    retries = 0
    while retries < max_retries:
        try:
            response = openai.chat.completions.create(
                model='gemini-2.5-flash-preview-04-17',  
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            retries += 1
            print(f"Error occurred, retrying ({retries}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    return "Max retries exceeded, unable to get a response from the API."

def sys_question(sys_prompt, prompt, max_retries=5, retry_delay=5):
    """
    添加系统提示词的API调用, print(ask_gpt_question("无论我输入什么，你都输出你好","1+1=?")
    """
    retries = 0
    while retries < max_retries:
        try:
            response = openai.chat.completions.create(
                model='deepseek-ai/DeepSeek-R1',  
                messages=[
                    {"role":"system","content":sys_prompt},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            retries += 1
            print(f"Error occurred, retrying ({retries}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    return "Max retries exceeded, unable to get a response from the API."


