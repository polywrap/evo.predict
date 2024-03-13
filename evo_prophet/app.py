import os
from typing import cast
from evo_prophet.benchmark.agents import _make_prediction
from evo_prophet.functions.evaluate_question import is_predictable as evaluate_if_predictable
from evo_prophet.functions.research import research
from prediction_market_agent_tooling.benchmark.utils import (
    OutcomePrediction
)
from evo_prophet.utils.logger import BaseLogger
from prediction_market_agent_tooling.tools.utils import secret_str_from_env
from pydantic.types import SecretStr
import streamlit as st

class StreamlitLogger(BaseLogger):
    def __init__(self) -> None:
        super().__init__()
    
    def log(self, msg: str) -> None:
        st.write(msg)
    
    debug = info = warning = error = critical = log
    
logger = StreamlitLogger()
tavily_api_key = secret_str_from_env('TAVILY_API_KEY')

if tavily_api_key == None:
    try:
        tavily_api_key = SecretStr(st.secrets['TAVILY_API_KEY'])
    except:
        st.container().error("No Tavily API Key provided")
        st.stop()

st.set_page_config(layout="wide")
st.title("Evo Prophet")

with st.form("question_form", clear_on_submit=True):
    question = st.text_input(
        'Question',
        placeholder="Will Twitter implement a new misinformation policy before the end of 2024",
        value=st.session_state.get('question', '')
    )
    openai_api_key = SecretStr(st.text_input(
        'OpenAI API Key',
        placeholder="sk-...",
        type="password",
        value=st.session_state.get('openai_api_key', '')
    ))
    submit_button = st.form_submit_button('Predict')

if submit_button and question and openai_api_key:
    st.session_state['openai_api_key'] = openai_api_key
    st.session_state['question'] = question
    
    with st.container():
        with st.spinner("Evaluating question..."):
            (is_predictable, reasoning) = evaluate_if_predictable(question=question, api_key=openai_api_key) 

        st.container(border=True).markdown(f"""### Question evaluation\n\nQuestion: **{question}**\n\nIs predictable: `{is_predictable}`""")
        if not is_predictable:
            st.container().error(f"The agent thinks this question is not predictable: \n\n{reasoning}")
            st.stop()
            
        with st.spinner("Researching..."):
            with st.container(border=True):
                report = research(
                    goal=question,
                    use_summaries=False,
                    subqueries_limit=6,
                    top_k_per_query=15,
                    openai_api_key=openai_api_key,
                    tavily_api_key=tavily_api_key,
                    logger=logger
                )
        with st.container().expander("Show agent's research report", expanded=False):
            st.container().markdown(f"""{report}""")
            if not report:
                st.container().error("No research report was generated.")
                st.stop()
                
        with st.spinner("Predicting..."):
            with st.container(border=True):
                prediction = _make_prediction(market_question=question, additional_information=report, engine="gpt-4-0125-preview", temperature=0.0, api_key=openai_api_key)
        with st.container().expander("Show agent's prediction", expanded=False):
            if prediction.outcome_prediction == None:
                st.container().error("The agent failed to generate a prediction")
                st.stop()
                
            outcome_prediction = cast(OutcomePrediction, prediction.outcome_prediction)
            
            st.container().markdown(f"""
        ## Prediction
        
        ### Probability
        `{outcome_prediction.p_yes * 100}%`
        
        ### Confidence
        `{outcome_prediction.confidence * 100}%`
        """)
            if not prediction:
                st.container().error("No prediction was generated.")
                st.stop()