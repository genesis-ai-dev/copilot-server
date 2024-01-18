from typing import Callable
from pygls.server import LanguageServer

from lsprotocol.types import (
    Range,
    Position,
    TextEdit,
    WorkspaceEdit,
    CompletionParams,
    CodeAction,
    CodeActionKind,
    CodeActionParams,
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionKind,
    CodeActionOptions,
    CodeActionParams,
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
)
import webbrowser

class LineEdit:
    def __init__(self, message, edit):
        self.message = message
        self.edit = edit

    def __getitem__(self, key):
        if key == 'message':
            return self.message
        elif key == 'edit':
            return self.edit


class Ideas:
    def __init__(self, server: LanguageServer, line_edits: list[Callable], kind=CodeActionKind.RefactorInline):
        """
        Initializes an Ideas object.

        Parameters:
        - server (LanguageServer): The LanguageServer instance to handle language-related features.
        - line_edits (list[Callable]): List of functions to suggest edits for each line in a range.
        - kind (CodeActionKind, optional): The kind of code action. Default is CodeActionKind.RefactorInline.

        Returns:
        None
        """
        self.server = server
        self.line_edits = line_edits
        assert kind in CodeActionKind, f"Parameter 'kind' must be in the enum `lsprotocol.types.CodeActionKind`, you passed '{kind}'."
        self.kind = kind
        
        @server.feature(
            TEXT_DOCUMENT_CODE_ACTION,
            CodeActionOptions(code_action_kinds=[kind]),
        )
        def check_all(params: CodeAction):
            """
            Callback function for text document code action feature.

            Parameters:
            - params (CodeAction): The parameters containing information about the code action request.

            Returns:
            List[CodeAction]: The list of code action items.
            """
            document_uri = params.text_document.uri
            document = self.server.workspace.get_document(document_uri)
            

            items = []
            for line_edit in self.line_edits:
                items += self.idea(params, line_edit)
            return items
        self.check_all = check_all


    def idea(self, params: CodeActionParams, line_edit: Callable):
        """
        Generates a list of code actions based on line edits.

        Parameters:
        - params (CodeActionParams): The parameters containing information about the code action request.
        - line_edit (Callable): The function to suggest edits for each line in a range.

        Returns:
        List[CodeAction]: The list of code action items.
        """
        items = []
        document_uri = params.text_document.uri
        document = self.server.workspace.get_document(document_uri)

        start_line = params.range.start.line
        end_line = params.range.end.line

        lines = document.lines[start_line : end_line + 1]
        for idx, line in enumerate(lines):
            data = line_edit(line)
            if data: # All line_edit functions must return false if they are unused otherwise follow the schema
                assert data.__class__ == LineEdit, "You're line edit function must return either a valid LineEdit or bool: False"
                range_ = Range(
                    start=Position(line=start_line + idx, character=0),
                    end=Position(line=start_line + idx, character=len(line) - 1),
                )
                text_edit = TextEdit(range=range_, new_text=data['edit'])

                action = CodeAction(
                    title=data['message'],
                    kind=CodeActionKind.RefactorInline,
                    edit=WorkspaceEdit(changes={document_uri: [text_edit]}),
                )
                items.append(action)

        return items

    
class Completion:
    def __init__(self, server, completion_functions, trigger_characters=[' ']):
        """
        Class to handle text document completion using a list of completion functions.
        
        :param server: A pygls server instance
        :type server: LanguageServer
        :param completion_functions: A list of completion functions to use for generating completions.
        :type completion_functions: List[Callable]
        """

        self.server = server
        self.completion_functions = completion_functions
        self.trigger_characters = trigger_characters

        @server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=trigger_characters))
        def check_all(params: CompletionParams):
            document = server.workspace.get_document(params.text_document.uri)
            edits = [CompletionItem(label=item['message'], text_edit=TextEdit(
                range=Range(
                    start=params.position,
                    end=Position(line=params.position.line, character=params.position.character + 5) # Adjust the range as needed
                ),
                new_text=f"{item['edit']}"
            )) for item in [completion_function(lines=document.lines, current_line=params.position.line) for completion_function in self.completion_functions] if item]

            return CompletionList(
                is_incomplete=False,
                items=edits
            )
        self.check_all = check_all 