from typing import Union
from pygls.server import LanguageServer
import wildebeest.wb_analysis as analyze
import base_actions as base_actions
from lsprotocol.types import Position

server = LanguageServer("code-action-server", "v0.1")

def check1(text: str) -> Union[dict, bool]:
    if 'Jesus' not in text:
        edit = text.strip() + " Jesus!"
        line_edit = base_actions.LineItem(message='You never mentioned Jesus', edit=edit)
        return line_edit
    else:
        return False


def check2(text: str) -> Union[dict, bool]:
    upper_text = text.upper()
    if upper_text != text:
        line_edit = base_actions.LineItem(message='The text should be in all caps', edit=upper_text)
        return line_edit
    else:
        return False
    


def completion1(lines: list[str], current_line: int):
    if lines[current_line].strip().endswith("The"):
        line_edit = base_actions.LineItem(message='test', edit='test')
        return line_edit
    return False

def diagnotic1(lines: list[str]):
    diagnostics = []
    for line in lines:
        summary = analyze.process(string = line).summary_list_of_issues()   
        if summary:
            diagnostics.append(base_actions.LineItem(message=", ".join(summary), edit=None, source='Wildebeest', start=Position(line=lines.index(line), character=0), end=Position(line=lines.index(line), character=len(line))))
    if diagnostics:
        return diagnostics
    return False

base_actions.Ideas(server, line_edits=[check1, check2])
base_actions.Completion(server, completion_functions=[completion1])
base_actions.Diagnostics(server, diagnostic_functions=[diagnotic1])

if __name__ == "__main__":
    print('running:')
    server.start_io()