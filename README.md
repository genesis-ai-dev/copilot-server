# Copilot Server
This VSCode extension provides a Language Server written in Python. It includes code actions that can suggest edits and provide autocompletion for text documents within the VSCode environment. Lots more will added on top of this, but for a start this seems helpful.
## Install needed extensions:
1. Install Pylance and Python from the Microsoft vscode extension store.
2. Install `scripture-language-support` also from the extension store.
3. Intalling the `codex-editor` extension (this will take a bit more effort).

First, clone the repo `git clone https://github.com/genesis-ai-dev/codex-editor` and cd to that directory. Next, run `npm install`, `npm run compile` and `vsce package` in that order (ignore the warnings for `vsce`). If it is not yet installed, run `npm install -g vsce`.

This will create a `codex-editor.vsix` file. To add this as an extension in vscode, run `code --install-extension codex-editor.vsix` or open the extensions tab in vscode, select the three dots in the top right corner and click `Install from VSIX`.

## Development Setup

To contribute to this extension, clone the repository, and ensure you have the necessary dependencies installed:

1. Ensure you have all required extensions.
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
## Documentation

The `base_actions` module provides two classes, `Ideas` and `Completion`, that can be used to handle language-related features in a Language Server.

### `Ideas` Class

The `Ideas` class is used to generate a list of code actions based on line edits. It takes the following parameters:

- `server` (LanguageServer): The `LanguageServer` instance to handle language-related features.
- `line_edits` (list[Callable]): List of functions to suggest edits for each line in a range.
- `kind` (CodeActionKind, optional): The kind of code action. Default is `CodeActionKind.RefactorInline`.

#### Methods

##### `__init__(self, server: LanguageServer, line_edits: list[Callable], kind=CodeActionKind.RefactorInline)`

Initializes an `Ideas` object.

Parameters:
- `server` (LanguageServer): The `LanguageServer` instance to handle language-related features.
- `line_edits` (list[Callable]): List of functions to suggest edits for each line in a range.
- `kind` (CodeActionKind, optional): The kind of code action. Default is `CodeActionKind.RefactorInline`.

Returns:
None

##### `idea(self, params: CodeActionParams, line_edit: Callable)`

Generates a list of code actions based on line edits.

Parameters:
- `params` (CodeActionParams): The parameters containing information about the code action request.
- `line_edit` (Callable): The function to suggest edits for each line in a range.

Returns:
List[CodeAction]: The list of code action items.

##### `check_all(params: CodeAction)`

Callback function for the text document code action feature.

Parameters:
- `params` (CodeAction): The parameters containing information about the code action request.

Returns:
List[CodeAction]: The list of code action items.

### `Completion` Class

The `Completion` class is used to handle text document completion using a list of completion functions. It takes the following parameters:

- `server` (LanguageServer): A `pygls` server instance.
- `completion_functions` (list[Callable]): A list of completion functions to use for generating completions.
- `trigger_characters` (list[str], optional): A list of characters that trigger completion. Default is `[' ']`.

#### Methods

##### `__init__(self, server, completion_functions, trigger_characters=[' '])`

Class to handle text document completion using a list of completion functions.

Parameters:
- `server` (LanguageServer): A `pygls` server instance.
- `completion_functions` (list[Callable]): A list of completion functions to use for generating completions.
- `trigger_characters` (list[str], optional): A list of characters that trigger completion. Default is `[' ']`.

Returns:
None

##### `check_all(params: CompletionParams)`

Callback function for the text document completion feature.

Parameters:
- `params` (CompletionParams): The parameters containing information about the completion request.

Returns:
CompletionList: The list of completion items.

### Usage Example (from servers/server.py)

```python
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
```

In the above example, the `Ideas` class is used to suggest code actions based on line edits. The `check1` and `check2` functions are provided as line edit functions. The `Completion` class is used to handle text document completion, and the `completion1` function is provided as the completion function.

## Running the Language Server

To run the vscode extiontion, **make sure you are in the correct workspace**, and then press `fn+f5` (or whatever is used on your OS).

The server should start up, if not most errors seem to come from accidentally being in the wrong workspace (this is easy to accidentally do as the extention will open its own vscode instance which will look similar to the one you start in).

## TODO:
(no specific order)
- Add Wildebeest (starting)
- `.codex` and `.scripture` support etc... (mostly done, but each function should define which it applies to)
- Extend language server beyond autocomplete and code actions...

- Look into [pygls async usage](https://pygls.readthedocs.io/en/v0.11.2/pages/advanced_usage.html#asynchronous-functions-coroutines) and [pygls threading](https://pygls.readthedocs.io/en/v0.11.2/pages/advanced_usage.html#threaded-functions) where they might be helpful to make the experience smoother (e.g waiting for an LLM to generate a token shouldn't block the rest of the server...)

- Modify `/servers/workspace` to adhere to whatever structure we want our projects to use. (good for now)
- Linguistic anomaly detection...
- Add more to the TODO...