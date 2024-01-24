from typing import Callable
from pygls.server import LanguageServer
from lsprotocol.types import Range, Position, TextEdit

import lsprotocol.types as lsp_types


class ServerFunctions:
    def __init__(self, server):
        self.server = server
        self.completion_functions = []
        self.diagnostic_functions = []
        self.action_functions = []

        self.completion = None
        self.diagnostic = None
        self.action = None
    
    def add_diagnostic(self, function: Callable, severity: lsp_types.DiagnosticSeverity = lsp_types.DiagnosticSeverity.Warning):
        self.diagnostic_functions.append((function, severity))
    def add_completion(self, function: Callable, kind: lsp_types.CompletionItemKind = lsp_types.CompletionItemKind.Text):
        self.completion_functions.append((function, kind))
    def add_action(self, function: callable, kind: lsp_types.CodeAction = lsp_types.CodeActionKind.QuickFix):
        self.action_functions.append((function, kind))

    def start(self):
        @self.server.feature(
            lsp_types.TEXT_DOCUMENT_CODE_ACTION,
            lsp_types.CodeActionOptions(code_action_kinds=[action[1] for action in self.action_functions]),
        )
        def actions(params: lsp_types.CodeAction):
            items = []
            document_uri = params.text_document.uri
            document = self.server.workspace.get_document(document_uri)

            start_line = params.range.start.line
            end_line = params.range.end.line

            lines = document.lines[start_line : end_line + 1]
            for idx, line in enumerate(lines):
                range = Range(
                        start=Position(line=start_line + idx, character=0),
                        end=Position(line=start_line + idx, character=len(line) - 1),
                    )
                for completion_function in self.completion_functions:
                    items.extend(completion_function[0](params, range))
            return items
        self.action = actions

        
