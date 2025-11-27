import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import yaml
import requests # <-- Наша новая библиотека
import base64   # <-- Встроенная библиотека для декодирования ответа от GitHub
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

def get_code_from_github(github_url):
    """
    Скачивает содержимое файла из репозитория GitHub по URL.
    """
    print(f"Скачиваю код с GitHub: {github_url}")
    # Преобразуем обычный URL в URL для API
    # Пример: https://github.com/user/repo/blob/main/path/to/file.py
    # Станет: https://api.github.com/repos/user/repo/contents/path/to/file.py
    api_url = github_url.replace("github.com", "api.github.com/repos").replace("/blob/", "/contents/")
    
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Проверяем, что запрос прошел успешно (код 200)
        
        data = response.json()
        
        # GitHub API возвращает содержимое файла в кодировке base64
        if 'content' in data:
            file_content_base64 = data['content']
            # Декодируем содержимое из base64 в обычный текст
            decoded_content = base64.b64decode(file_content_base64).decode('utf-8')
            return decoded_content
        else:
            print("Ошибка: 'content' не найден в ответе от API GitHub.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к GitHub API: {e}")
        return None

def load_config(path):
    # ... (эта функция остается без изменений) ...
    print(f"Загружаю конфигурацию из {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_prompt_from_config(config, prompt_template):
    # ... (эта функция остается без изменений) ...
    print("Генерирую финальный промпт из конфига и шаблона...")
    final_prompt = prompt_template.replace('{{language}}', config['context']['language'])
    final_prompt = final_prompt.replace('{{coding_standard}}', config['context']['coding_standard'])
    final_prompt = final_prompt.replace('{{purpose}}', config['context']['purpose'])
    rules_text = ""
    for category, rules_list in config['rules'].items():
        rules_text += f"### {category}\n"
        for rule in rules_list:
            rules_text += f"- {rule}\n"
    final_prompt = final_prompt.replace('{{rules_list}}', rules_text)
    return final_prompt

def main():
    print("--- ЗАПУСК КОНФИГУРИРУЕМОГО AI КОД-РЕВЬЮЕРА ---")
    
    # --- ИЗМЕНЕНИЕ 1: Определяем, откуда брать код ---
    # Вставьте сюда URL файла с GitHub для анализа
    # Для примера, возьмем заведомо плохой код из тестового репозитория
    github_file_url = "https://github.com/test-repo-auditor/bad-code-example/blob/main/vulnerable.py"
    
    # Получаем код с GitHub
    code_snippet = get_code_from_github(github_file_url)
    
    # Если код не удалось скачать, прекращаем работу
    if code_snippet is None:
        print("Не удалось получить код. Завершение работы.")
        return

    config = load_config("config.yml")
    with open("prompt_template.txt", 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    final_prompt = generate_prompt_from_config(config, prompt_template)
    final_prompt = final_prompt.replace('{CODE_HERE}', code_snippet)
    
    # ... (вся остальная часть с загрузкой модели и генерацией остается без изменений) ...
    model_name = "codellama/CodeLlama-7b-Instruct-hf" # Используем лучшую модель
    print(f"Использую модель: {model_name}")

    hf_token = os.getenv("HF_TOKEN")

    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)

    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, device_map="auto", token=hf_token)
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    print("Модель и токенизатор загружены.")
    
    stop_token_id = tokenizer.convert_tokens_to_ids("<|file_separator|>")
    
    print("Отправляю код на ревью AI. Ожидайте...")
    
    input_ids = tokenizer(final_prompt, return_tensors="pt").to("cuda")
    prompt_length = input_ids['input_ids'].shape[1]

    output_ids = model.generate(
        **input_ids, 
        max_new_tokens=config['model_settings']['max_new_tokens'], 
        do_sample=True, 
        temperature=config['model_settings']['temperature'],
        eos_token_id=stop_token_id
    )
    
    clean_output = tokenizer.decode(output_ids[0][prompt_length:], skip_special_tokens=True)
    
    print("\n" + "="*50)
    print("--- РЕЗУЛЬТАТ РЕВЬЮ ---")
    print("="*50 + "\n")
    print(clean_output.strip())

if __name__ == "__main__":
    main()