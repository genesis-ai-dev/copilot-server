# Python Language Server for vscode (so far)
This VSCode extension provides a Language Server written in Python. It includes code actions that can suggest edits and provide autocompletion for text documents within the VSCode environment. Lots more will added on top of this, but for a start this seems helpful.

## Development Setup

To contribute to this extension, clone the repository, and ensure you have the necessary dependencies installed:

1. Ensure you have the Python extention for vscode.
2. Clone this repo:
```bash
git clone https://github.com/dadukhankevin/Language-Server-for-Translation
```
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Implement additional checks or completion functions as needed.
4. Add your functions to the respective `Ideas` or `Completion` class instances.

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

### Autocompletion

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

### `Ideas`

This class is responsible for providing code actions. When initialized, it takes a list of functions that suggest edits and registers a callback to the code action feature of the Language Server Protocol.

### `Completion`

This class handles autocompletion features. It accepts a list of functions that provide completion suggestions and registers a callback to the completion feature of the Language Server Protocol.

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