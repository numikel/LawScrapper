from typing import Annotated, Literal
from typing_extensions import TypedDict
from send_notification import send_notification
from langchain.tools import StructuredTool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
from scrapper import JOLScrapper

scrapper = JOLScrapper()

load_dotenv()

class State(TypedDict):
    acts: list
    current_act: int

def no_acts_notification(state: State) -> State:
    print("Sending notification...")
    send_notification(
        subject="[LawScrapper] Brak nowych aktów prawnych",
        title="Brak nowych aktów prawnych",
        body="Brak nowych aktów prawnych z zakresu bezpieczeństwa pożarowego."
    )
    return {
        "acts": [],
        "current_act": None
    }

def process_act(state: State) -> State:
    print("Processing act... " + str(state.get("current_act")))
    # print(state.get("acts")[state.get("current_act")]["title"])
    return {
        "current_act": state.get("current_act") + 1
    }

def get_new_acts(state: State) -> State:
    # scrapper.get_acts_from_last_month(keywords=["przeciwpożarowa ochrona"])
    scrapper.get_acts_from_last_week()
    # scrapper.get_acts_list(keywords=["przeciwpożarowa ochrona"])

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
   return {}

def prepare_summary_notification(state: State) -> State:
    print("Sending notification...")
    rows = ""
    for index, act in enumerate(state.get("acts"), 1):
       rows += f"""<tr style="">
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{index}</td>
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('title')}</td>
            <!-- <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">'llm_summary'</td> -->
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('promulgation')}</td>
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('announcementDate')}</td>
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('entryIntoForce')}</td>
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('keywords')}</td>
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">
                <table class="btn btn-primary" role="presentation" border="0" cellpadding="0" cellspacing="0"
                    style="border-radius: 6px; border-collapse: separate !important;">
                    <tbody>
                        <tr>
                            <td style="line-height: 24px; font-size: 12px; border-radius: 6px; margin: 0;"
                                align="center" bgcolor="#0d6efd">
                                <a href="{act.get('pdf') if act.get('pdf') else act.get('html')}"
                                    style="color: #ffffff; font-size: 12px; font-family: Helvetica, Arial, sans-serif; text-decoration: none; border-radius: 6px; line-height: 20px; display: block; font-weight: normal; white-space: nowrap; background-color: #0d6efd; padding: 8px 12px; border: 1px solid #0d6efd;">Pokaż</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>"""
    
    table = f""" <table class="table table-striped table-bordered" border="0" cellpadding="0" cellspacing="0"
        style="width: 100%; max-width: 100%; border: 1px solid #e2e8f0;">
        <thead>
            <tr>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">L.p</th>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Tytu&#322; aktu</th>
                <!-- <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Podsumowanie</th> -->
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Data og&#322;oszenia</th>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Data wydania</th>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Data wej&#347;cia w &#380;ycie</th>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">S&#322;owa kluczowe</th>
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Tre&#347;&#263; aktu</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>"""
    
    send_notification(
        subject="[LawScrapper] Zmiany prawne w ostatnim tygodniu",
        title="Lista aktów prawnych, które weszły w życie w ostatnim tygodniu.",
        body= "Poniżej lista aktów prawnych, które weszły w życie w ostatnim tygodniu",
        table = table
    )
    return {}
  
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
workflow.add_node("prepare_summary_notification", prepare_summary_notification)
workflow.add_conditional_edges("get_new_acts", has_new_acts)
workflow.add_conditional_edges("process_act", has_more_acts)
workflow.add_edge(START, "get_new_acts")
workflow.add_edge("no_acts_notification", END)
workflow.add_edge("prepare_summary", "prepare_summary_notification")
workflow.add_edge("prepare_summary_notification", END)

graph = workflow.compile()

result = graph.invoke({
    "acts": [],
    "current_act": 0
}, {"recursion_limit": 100})

print(result)