from typing import Union
from pygls.server import LanguageServer
import wildebeest.wb_analysis as analyze
import base_actions as base_actions
from lsprotocol.types import Position, DidCloseTextDocumentParams, TEXT_DOCUMENT_DID_CLOSE
import embedding_tools as emb
import urllib.parse
import re

is_embedding = ""
last_result = ""
server = LanguageServer("code-action-server", "v0.1")
database = None


def is_bible_verse(reference):
    # Define a regex pattern for Bible verse references
    pattern = re.compile(r'^\d*[A-Za-z]+\s\d+:\d+')

    # Check if the reference matches the pattern
    return bool(pattern.match(reference))


def uri_to_filepath(uri):
    # Decode the URL
    decoded_url = urllib.parse.unquote(uri)

    # Remove the scheme and the first slash if present
    if decoded_url.startswith('vscode-notebook-cell:/'):
        decoded_url = decoded_url[len('vscode-notebook-cell:/'):]

    # Remove the first slash if present
    if decoded_url.startswith('/'):
        decoded_url = decoded_url[1:]

    return decoded_url.split("#")[0]


def check2(text: str) -> Union[dict, bool]:
    upper_text = text.upper()
    if upper_text != text:
        return base_actions.LineItem(message='The text should be in all caps', edit=upper_text)
    return False


# def completion1(lines: list[str], current_line: int):
#     if lines[current_line].strip().endswith("The"):
#         return base_actions.LineItem(message='test', edit='test')
#     return False


def diagnotic1(lines: list[str]):
    diagnostics = []
    for line in lines:
        summary = analyze.process(string=line).summary_list_of_issues()
        if summary:
            diagnostics.append(base_actions.LineItem(
                message=", ".join(summary),
                edit=None,
                source='Wildebeest',
                start=Position(line=lines.index(line), character=0),
                end=Position(line=lines.index(line), character=len(line))
            ))
    return diagnostics if diagnostics else False


def embed_document(params):
    global database
    db_path = server.workspace.root_path + "/" + "database"
    path = params[0]['fsPath']
    if ".codex" in path:
        if not database:
            database = emb.DataBase(db_path)
        server.show_message(message="Embedding document.")
        database.upsert_codex_file(path=path)
        server.show_message(
            message=f"The Codex file '{path}' has been upserted into 'database'")
    else:
        server.show_message(message="Current file must be .codex")


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
async def on_close(ls, params: DidCloseTextDocumentParams):
    global is_embedding
    path = uri_to_filepath(params.text_document.uri)

    if path != is_embedding:  # in case it fires multiple times
        embed_document([{'fsPath': path}])
        is_embedding = path
        server.show_message("closed file")


def embed_document_command(params):
    return embed_document(params)


def embed_idea(query: str):
    global database, last_result
    db_path = server.workspace.root_path + "/" + "database"
    if not database:
        server.show_message(
            message="NLP features are loading, this may take a moment.")
        database = emb.DataBase(db_path)
        server.show_message(message="NLP features have loaded.")
    if not is_bible_verse(query):
        result = database.search(query, limit=1)

        if result:
            result = result[0]['text']
            line_edit = base_actions.LineItem(
                message=str(result), edit=result)
            last_result = line_edit
            return line_edit
    return False


server.command("pygls.server.EmbedDocument")(embed_document_command)

base_actions.Ideas(server, line_edits=[embed_idea])
# base_actions.Completion(server, completion_functions=[completion1])
base_actions.Diagnostics(server, diagnostic_functions=[diagnotic1])

if __name__ == "__main__":
    print('running:')
    server.start_io()
