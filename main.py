from typing import Literal
from typing_extensions import TypedDict
from send_notification import send_notification
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from scrapper import LawScrapper
from model import LegalActSummarizer

scrapper = LawScrapper()

load_dotenv()

class State(TypedDict):
    """
    This module defines a LangGraph-based workflow for fetching recent legal acts,
    summarizing them using an LLM (Claude), and notifying users via email.
    """
    keywords: list
    acts: list
    current_act: int

def no_acts_notification(state: State) -> State:
    """
    Sends a notification email informing that no new legal acts were found.

    Parameters:
        state (State): Current workflow state.

    Returns:
        State: Unchanged state after notification.
    """
    print("Sending notification...")
    send_notification(
        subject="[LawScrapper] Brak nowych aktów prawnych",
        title="Brak nowych aktów prawnych",
        body="Brak nowych aktów prawnych w wybranym zakresie dat lub zgodnie z ustawionym słowem kluczowym"
    )
    return state

def process_act(state: State) -> State:
    """
    Processes the current act in the state by downloading its PDF content,
    summarizing it with the LegalActSummarizer (LLM), and storing the result.

    Parameters:
        state (State): Workflow state containing the list of acts and the current index.

    Returns:
        State: Updated state with summary for the current act and incremented index.
    """
    print(f'{(state["current_act"] + 1)}/{len(state["acts"])} Processing act... ')
    act = state["acts"][state["current_act"]]
    summarizer = LegalActSummarizer()
    try:
        content = summarizer.get_act_content(act["pdf"])
        summary = summarizer.process_with_llm(content)
    except Exception as e:
        print(f"Error while summarizing act: {e}")
        summary = "Summary unavailable"

    act["summary"] = summary
    state["current_act"] = state["current_act"] + 1
    return state

def get_new_acts(state: State) -> State:
    """
    Fetches new legal acts from the last week based on the provided keyword.

    Parameters:
        state (State): Workflow state with keyword input.

    Returns:
        State: Updated state with a list of formatted legal acts.
    """
    keywords = None
    if (state["keywords"]): 
       keywords = state["keywords"]
    acts = scrapper.get_acts_from_last_week(keywords=keywords)
    state["acts"] = scrapper.get_formatted_list()
    return state

def has_new_acts(state: State)->Literal["no_acts_notification", "process_act"]:
    """
    Decision function for LangGraph:
    Determines if there are any acts to process.

    Parameters:
        state (State): Workflow state.

    Returns:
        str: "process_act" if acts exist, otherwise "no_acts_notification".
    """
    if state.get("acts"):
      return "process_act"
    else:
      return "no_acts_notification"

def prepare_summary_notification(state: State) -> State:
    """
    Prepares and sends a summary notification email containing a formatted HTML table
    with all processed acts and their summaries.

    Parameters:
        state (State): Workflow state containing processed legal acts.

    Returns:
        State: Unchanged state after sending summary.
    """
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
            <td class="text-xs"
                style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border: 1px solid #e2e8f0;"
                align="left" valign="top">{act.get('summary')}</td>
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
                <th class="text-xs"
                    style="line-height: 14.4px; font-size: 12px; margin: 0; padding: 12px; border-color: #e2e8f0; border-style: solid; border-width: 1px 1px 2px;"
                    align="left" valign="top">Podsumowanie</th>
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
        title="Lista aktów prawnych, które weszły w życie w ostatnim tygodniu",
        body= "Poniżej lista aktów prawnych, które weszły w życie w ostatnim tygodniu",
        table = table
    )
    return state
  
def has_more_acts(state: State)->Literal["prepare_summary_notification", "process_act"]:
    """
    Decision function for LangGraph:
    Determines whether there are more acts to process.

    Parameters:
        state (State): Workflow state containing the list and current act index.

    Returns:
        str: "process_act" if more acts are left, otherwise "prepare_summary_notification".
    """
    if state.get("current_act") < len(state.get("acts")):
      return "process_act"
    else:
      return "prepare_summary_notification"

workflow = StateGraph(State)

workflow.add_node("get_new_acts", get_new_acts)
workflow.add_node("no_acts_notification", no_acts_notification)
workflow.add_node("process_act", process_act)
workflow.add_node("prepare_summary_notification", prepare_summary_notification)
workflow.add_conditional_edges("get_new_acts", has_new_acts)
workflow.add_conditional_edges("process_act", has_more_acts)
workflow.add_edge(START, "get_new_acts")
workflow.add_edge("no_acts_notification", END)
workflow.add_edge("prepare_summary_notification", END)

graph = workflow.compile()

result = graph.invoke({
    "acts": [],
    "current_act": 0,
    "keywords": [
        "bhp", 
        "przeciwpożarowa ochrona",
        "czynniki szkodliwe dla zdrowia", 
        "dozór techniczny", 
        "hałas i wibracje", 
        "inspekcja pracy",
        "odzież ochronna, robocza i sprzęt ochrony osobistej", 
        "ochotnicza straż pożarna",
        "Państwowa Straż Pożarna", 
        "Straż Pożarna",
        "warunki sanitarne", 
        "warunki szkodliwe", 
        "warunki uciążliwe", 
        "wypadki przy pracy"
    ]
}, {"recursion_limit": 100})
print(result)
