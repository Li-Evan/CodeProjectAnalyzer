import os
import json
import concurrent.futures
import datetime
from util import *

def get_file_structure(directory):
    structure = []
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level
        if any(file.endswith('.py') for file in files):
            structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                structure.append(f"{sub_indent}{file}")
    structure = '\n'.join(structure)
    return structure



def _get_file_number(directory, file_type='.py'):
    number = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(file_type):
                number += 1
    # print(number)
    return number


def get_file_logic(directory, structure, promgram_language='python'):
    total_context = CONTEXT_LENGTH
    total_number = _get_file_number(directory)
    single_limit = total_context // total_number

    total_code = ""

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    code = file.read()
                total_code += f"{file_name}的内容:\n\n"
                total_code += code[:single_limit]
                total_code += '\n\n'
                total_code += "=" * 100
                total_code += '\n\n'

    with open("prompt/module_logic.txt", 'r', encoding='utf-8') as file:
        prompt = file.read().format(
            program_language=promgram_language,
            structure=structure,
            code=total_code
        )
    return talk_llm(prompt)
    # with open("total_code.txt", 'w', encoding='utf-8') as file:
    #     file.write(total_code)


def detail_analyze_file(file_path, structure, logic, language='中文'):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            code = file.read()
        with open("prompt/detail_analysis.txt", 'r', encoding='utf-8', errors='ignore') as file:
            prompt = file.read().format(
                language=language,
                structure=structure,
                logic=logic,
                code=code
            )
        # 解析代码
        return talk_llm(prompt[:CONTEXT_LENGTH])
    except Exception as e:
        return f"无法分析文件 {file_path}: {str(e)}"


def main(directory):
    result = {}
    print(f"正在分析项目 {directory}:")

    # 0. 获取整个项目的待分析文件数量
    analysis_number = _get_file_number(directory)
    result['analysis_number'] = analysis_number
    print(f"待分析文件数量: {analysis_number}")

    # 1. 获取文件整体的结构
    print(f"正在分析文件结构:")
    code_structure = get_file_structure(directory)
    result['code_structure'] = code_structure
    # print(code_structure)

    # 2. 分析文件整体关系
    print("\n正在分析文件逻辑:")
    code_logic = get_file_logic(directory, code_structure)
    result['code_logic'] = code_logic

    # 3. 分析具体文件内容
    print("\n正在逐文件分析:")
    detail_analysis = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {
            executor.submit(detail_analyze_file, os.path.join(root, file), code_structure, code_logic): file
            for root, dirs, files in os.walk(directory)
            for file in files
            if file.endswith('.py')  # 这里你可以选择分析特定类型的文件
        }

        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                analysis = future.result()
                detail_analysis[file] = analysis
                # print(f"\n{file}分析结果:")
                # print(analysis)
            except Exception as e:
                print(f"无法分析文件 {file}: {str(e)}")

    result['detail_analysis'] = detail_analysis

    # 5. 保存结果
    project_name = os.path.basename(directory)
    today = datetime.datetime.now().date()
    output_name = f"{project_name}_{today.strftime('%Y%m%d')}.json"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_name)
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    directory = r"the directory path of your project that you want to analyze"
    main(directory)
