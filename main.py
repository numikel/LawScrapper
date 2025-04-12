from typing import Annotated, Literal
from typing_extensions import TypedDict
from send_notification import send_notification
from langchain.tools import StructuredTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os
from scrapper import JOLScrapper
import json

scrapper = JOLScrapper()

load_dotenv()

class State(TypedDict):
    acts: list
    current_act: int

def no_acts_notification(state: State) -> State:
    print("Sending notification...")
    send_notification(
        subject="[LawScrapper] Brak nowych aktów prawnych",
        body="Brak nowych aktów prawnych z zakresu bezpieczeństwa pożarowego."
    )
    return {
        "acts": [],
        "current_act": None
    }

def process_act(state: State) -> State:
    print("Processing act...")
    print(state.get("acts")[state.get("current_act")]["title"])
    return {
        "acts": state.get("acts"),
        "current_act": state.get("current_act") + 1
    }

def get_new_acts(state: State) -> State:
    # scrapper.get_acts_from_last_month(keywords=["przeciwpożarowa ochrona"])
    scrapper.get_acts_list(keywords=["przeciwpożarowa ochrona"])

    return {
        "acts": scrapper.get_formatted_list(),
        "current_act": 0
    }

def has_new_acts(state: State)->Literal["no_acts_notification", "process_act"]:
  if state.get("acts"):
    return "process_act"
  else:
    return "no_acts_notification"
  
def prepare_summary(state: State) -> State:
   print("Preparing summary...")
  
def has_more_acts(state: State)->Literal["prepare_summary", "process_act"]:
  if state.get("current_act") < len(state.get("acts")):
    return "process_act"
  else:
    return "prepare_summary"

workflow = StateGraph(State)

workflow.add_node("get_new_acts", get_new_acts)
workflow.add_node("no_acts_notification", no_acts_notification)
workflow.add_node("process_act", process_act)
workflow.add_node("prepare_summary", prepare_summary)
workflow.add_conditional_edges("get_new_acts", has_new_acts)
workflow.add_conditional_edges("process_act", has_more_acts)
workflow.add_edge(START, "get_new_acts")
workflow.add_edge("no_acts_notification", END)
workflow.add_edge("process_act", END)

graph = workflow.compile()

result = graph.invoke({
    "acts": [],
    "current_act": 0
})

print(result)