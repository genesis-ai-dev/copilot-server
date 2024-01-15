# Python Language Server for vscode (so far)
This VSCode extension provides a Language Server written in Python. It includes code actions that can suggest edits and provide autocompletion for text documents within the VSCode environment. Lots more will added on top of this, but for a start this seems helpful.
## Install needed extensions:
1. Install Pylance and Python from the Microsoft vscode extension store.
2. Install `scripture-language-support` also from the extension store.
3. Intalling the `codex-editor` extension (this will take a bit more effort).

First, clone the repo `git clone https://github.com/genesis-ai-dev/codex-editor` and cd to that directory. Next, run `npm install`, `npm run compile` and `vsce package` in that order (ignore the warnings for `vsce`). If it is not yet installed, run `npm install -g vsce`.

This will create a `codex-editor.vsix` file. To add this as an extension in vscode, run `code --install-extension codex-editor.vsix` or open the extensions tab in vscode, select the three dots in the top right corner and click `Install from VSIX`.
## Development Setup

To contribute to this extension, clone the repository, and ensure you have the necessary dependencies installed:

1. Ensure you have the Python extention for vscode.
2. Clone this repo:
```bash
git clone https://github.com/genesis-ai-dev/copilot-server.git
```
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Add the correct path to `servers/settings.json`
replace line 12:
    ```"pygls.server.cwd": "C:\\Users\\danie\\langserver\\servers"```
with:
    ```"pygls.server.cwd": "<Your path to server directory>"```
This is only needed due to a bug and relative paths and so on will work soon. Just don't accidentally push these changes.

4. Implement additional checks or completion functions as needed.
5. Add your functions to the respective `Ideas` or `Completion` class instances.

## Features

- **Actions**: Suggests edits for lines that do not meet certain criteria (e.g., mentioning specific words or phrases).
- **Autocompletion**: Offers completion suggestions for sentences or phrases when a trigger condition is met. This can be anything from simple autocomplete or suggesting words provided by an LLM.

### Actions

To add new "code" (but in this case text) actions, you can create functions that analyze text and suggest edits. These functions should return either a `LineEdit` object with a message and the suggested edit or `False` if no edit is necessary.

Example of a code action function:

```python
def my_custom_check(text: str) -> Union[dict, bool]:
    if 'condition' in text:
        # Return a suggested edit
        edit = text.replace('condition', 'replacement')
        line_edit = base_actions.LineEdit(message='Suggestion message', edit=edit)
        return line_edit
    else:
        # No edit needed
        return False
```

To register this action, add the function to the `Ideas` class instance in `server.py`:

```python
base_actions.Ideas(server, line_edits=[..., my_custom_check])
```

### Autocompletion (UPDATE: These should now return a LineEdit)

You can also create functions that provide completion suggestions based on the current text. These functions should return a list of strings representing suggested completions.

Example of a completion function:
(currently there is a bug where it only shows one suggestion, It was working but somehow it stopped 🤷‍♂️, it'll be fixed soon)
```python
def my_custom_completion(text: str):
    if text.endswith("Example"):
        # Any complex functionality here
        return [" completion 1", " completion 2", " completion 3"]
```

To register this completion, add the function to the `Completion` class instance in `server.py`:

```python
base_actions.Completion(server, [completion1, my_custom_completion])
```

## Classes
## `Ideas`

The `Ideas` class is designed to manage and provide code actions. It evaluates text against a set of provided functions to suggest potential edits to improve the translation or to enforce specific guidelines.

### Initialization:

```python
Ideas(server: LanguageServer, line_edits: list[Callable], kind: CodeActionKind = CodeActionKind.RefactorInline)
```

#### Parameters:

- `server` (`LanguageServer`): The LanguageServer instance that enables interaction with the client's language features.
- `line_edits` (`list[Callable]`): A list of functions that the server will use to check each line within the provided range for potential edits. Each function should accept a single `str` argument representing the line of text and return either a `LineEdit` object with suggested changes or `False` if no change is suggested.
- `kind` (`CodeActionKind`, optional): Specifies the kind of code action to be returned. Defaults to `CodeActionKind.RefactorInline`.

### Methods:

- `idea(params: CodeActionParams, line_edit: Callable) -> List[CodeAction]`: Generates code actions for the provided text range based on the given line edit function.

## `Completion`

The `Completion` class handles autocompletion suggestions. It calls a list of functions that return potential completions based on the current text context.

### Initialization:

```python
Completion(server: LanguageServer, completion_functions: list[Callable], call_only_until_first_valid: bool = False)
```

#### Parameters:

- `server` (`LanguageServer`): The LanguageServer instance that enables interaction with the client's language features.
- `completion_functions` (`list[Callable]`): A list of functions that provide completion suggestions. Each function should accept a `str` argument representing the current line and return a list of `str` with suggested completions.
- `call_only_until_first_valid` (`bool`, optional): If set to `True`, the completion process will stop after the first function returns a non-empty list of suggestions. Defaults to `False`.

### Methods:

- `complete(line: str) -> CompletionList`: Calls each function in `completion_functions` with the current line as the argument and aggregates the results into a `CompletionList`.
- `debug(line: str)`: A utility method for debugging that prints the labels of completion items for the given line.
### `LineEdit`

This helper class represents a suggested edit. It contains a message that describes the suggestion and the actual edit to be applied to the text.

## Running the Language Server

To run the vscode extiontion, **make sure you are in the correct workspace**, and then press `fn+f5` (or whatever is used on your OS).

The server should start up, if not most errors seem to come from accidentally being in the wrong workspace (this is easy to accidentally do as the extention will open its own vscode instance which will look similar to the one you start in).

## TODO:
(no specific order)
- Add Wildebeest
- `.codex` and `.scripture` support etc...
- Extend language server beyond autocomplete and code actions...
- Look into [pygls async usage](https://pygls.readthedocs.io/en/v0.11.2/pages/advanced_usage.html#asynchronous-functions-coroutines) and [pygls threading](https://pygls.readthedocs.io/en/v0.11.2/pages/advanced_usage.html#threaded-functions) where they might be helpful to make the experience smoother (e.g waiting for an LLM to generate a token shouldn't block the rest of the server...)
- Modify `/servers/workspace` to adhere to whatever structure we want our projects to use.
- Linguistic anomaly detection...
- Add more to the TODO...