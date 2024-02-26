import os
import uuid
import click
import time
from dotenv import load_dotenv
from evo_researcher.functions.make_prediction import make_prediction
from langchain_community.callbacks import get_openai_callback
from evo_researcher.functions.grade_info import grade_info
from evo_researcher.functions.research import research as evo_research

load_dotenv()

def create_output_file(info: str, report: str) -> str:
    outputs_dir = 'outputs'
    os.makedirs(outputs_dir, exist_ok=True)

    dir_name = os.path.join(outputs_dir, str(uuid.uuid4()))
    os.makedirs(dir_name, exist_ok=True)

    info_file_path = os.path.join(dir_name, 'information.txt')
    with open(info_file_path, 'w') as file:
        file.write(info)
    
    report_file_path = os.path.join(dir_name, 'report.md')
    with open(report_file_path, 'w') as file:
        file.write(report)
        
    return dir_name

def read_text_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

@click.group()
def cli() -> None:
    pass
    
@cli.command()
@click.argument('prompt')
def research(
    prompt: str
) -> None:
    start = time.time()
    with get_openai_callback() as cb:
        (report, chunks) = evo_research(goal=prompt, model="gpt-4-1106-preview", use_summaries=False)
        end = time.time()
        
        dir_name = create_output_file(chunks, report)
        output_file = "report.md"
    
    print(f"Prompt tokens: {cb.prompt_tokens} - Completion tokens: {cb.completion_tokens}")
    print(f"\n\nTime elapsed: {end - start}")
    
    print(f"\n\nTo evaluate the output, run:\n\npoetry run python ./evo_researcher/main.py evaluate '{prompt}' ./{dir_name}/{output_file}")
    print(f"\n\nTo make a prediction using this output, run:\n\npoetry run python ./evo_researcher/main.py predict '{prompt}' ./{dir_name}/{output_file}")
    
@cli.command()
@click.argument('prompt')
@click.argument('path')
def evaluate(prompt: str, path: str) -> None:
    information = read_text_file(path)
    scores = grade_info(question=prompt, information=information)
    print(scores)
    

@cli.command()
@click.argument('prompt')
@click.argument('path')
def predict(prompt: str, path: str) -> None:
    information = read_text_file(path)
    
    start = time.time()
    with get_openai_callback() as cb:
        prediction = make_prediction(prompt=prompt, additional_information=information)
    end = time.time()
    
    print(prediction)
    print(f"Prompt tokens: {cb.prompt_tokens} - Completion tokens: {cb.completion_tokens}")
    print(f"\n\nTime elapsed: {end - start}")

if __name__ == '__main__':
    cli()