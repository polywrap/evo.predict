import click
import time
from dotenv import load_dotenv
from evo_researcher.autonolas.research import research as research_autonolas
from evo_researcher.functions.research import research

load_dotenv()
AVAILABLE_AGENTS = ["autonolas", "evo"]
    
@click.command()
@click.option('--prompt',
              prompt='Prompt',
              required=True,
              help='Prompt')
@click.option('--agent',
              prompt=f"Agent to use ({AVAILABLE_AGENTS})",
              required=True,
              help='Agent')
def run(
    prompt: str,
    agent: str
):
    start = time.time()
    if agent == "autonolas":
        research_response = research_autonolas(prompt)
    elif agent == "evo":
        research_response = research(prompt)
    else:
        raise Exception(f"Invalid agent. Available agents: {AVAILABLE_AGENTS}")
    end = time.time()
    print(research_response)
    print(f"Time elapsed: {end - start}")

if __name__ == '__main__':
    run()