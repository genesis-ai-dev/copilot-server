from typing import Union
from pygls.server import LanguageServer
import base_actions as base_actions

server = LanguageServer("code-action-server", "v0.1")

def check1(text: str) -> Union[dict, bool]:
    if 'Jesus' not in text:
        edit = text.strip() + " Jesus!"
        line_edit = base_actions.LineEdit(message='You never mentioned Jesus', edit=edit)
        return line_edit
    else:
        return False


def check2(text: str) -> Union[dict, bool]:
    upper_text = text.upper()
    if upper_text != text:
        line_edit = base_actions.LineEdit(message='The text should be in all caps', edit=upper_text)
        return line_edit
    else:
        return False
    


def completion1(lines: list[str], current_line: int):
    if lines[current_line].strip().endswith("The"):
        line_edit = base_actions.LineEdit(message='test', edit='test')
        return line_edit
    return False

base_actions.Ideas(server, line_edits=[check1, check2])
base_actions.Completion(server, completion_functions=[completion1])

if __name__ == "__main__":
    print('running:')
    server.start_io()