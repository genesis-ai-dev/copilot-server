from typing import Callable
from pygls.server import LanguageServer
import webbrowser
from lsprotocol.types import (
    Range,
    Position,
    TextEdit,
    WorkspaceEdit,
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
    CompletionParams,
)


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
    def __init__(self, server: LanguageServer, completion_functions: list[Callable], call_only_until_first_valid: bool=False):
        """
        Initializes a Completion object.

        Parameters:
        - server (LanguageServer): The LanguageServer instance to handle language-related features.
        - completion_functions (list[Callable]): List of functions to provide completion suggestions.
        - call_only_until_first_valid (bool, optional): If True, stops calling completion functions after the first valid suggestion is found.

        Returns:
        None
        """
        self.server = server
        self.completion_functions = completion_functions
        self.call_only_until_first_valid = call_only_until_first_valid

        @server.feature(TEXT_DOCUMENT_COMPLETION)
        def check_all(params: CodeAction) -> CompletionList:
            document = server.workspace.get_document(params.text_document.uri)
            current_line = document.lines[params.position.line].strip()
            start_line = params.position.line
            range_ = Range(
                start=Position(line=start_line, character=0),
                end=Position(line=start_line, character=len(current_line)),
            )
            items = self.complete(current_line)
            new_items = []
            if items:
                for item in items.items:

                    # Use the correct character offset for TextEdit
                    text_edit = TextEdit(
                        range=range_,
                        new_text=current_line + item.label
                    )
                    item.text_edit = text_edit
                    item.kind = CompletionItemKind.Keyword
                return items
            return None
        self.check_all = check_all


    def complete(self, line:str) -> CompletionList:
        """
        Generates a list of completion items by calling each completion function.

        Parameters:
        - line (str): The current line for which completion items are requested.

        Returns:
        CompletionList: The list of completion items.
        """
        items = []
        for completion_function in self.completion_functions:
            out = completion_function(line)
            print(out)
            if out:
                items += [CompletionItem(label=word) for word in out]
                if len(items) != 0 and self.call_only_until_first_valid:
                    break
        if items:
            return CompletionList(is_incomplete=True, items=items)
        else:
            return None
    
    def debug(self, line: str) -> None:
        """
        Prints the labels of completion items generated for a given line.

        Parameters:
        - line (str): The line for which completion items are generated.

        Returns:
        None
        """
        items = self.complete(line)
        [print(word.label) for word in items]
