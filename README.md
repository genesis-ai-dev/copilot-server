# Language Server Protocol Extension with Python and VSCode

This README will guide you through the process of using the `ServerFunctions` class to extend the functionality of a Language Server Protocol (LSP) implementation using Python and Visual Studio Code (VSCode). The `ServerFunctions` class provides a way to add custom completion, diagnostic, and action features to your language server.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.7 or higher
- Visual Studio Code
- Install `scripture-language-support` from the extension store

## How it works:
1. First, you need to create an instance of `LanguageServer` from the `pygls` package:

    ```python
    from pygls.server import LanguageServer

    server = LanguageServer("your-language-server-name", "your-version")
    ```

2. Then, create an instance of `ServerFunctions` by providing the `server` object and a path to store project data (this is relative to the workspace):

    ```python
    from your_module import ServerFunctions

    server_functions = ServerFunctions(server=server, data_path='/path_to_project_data')
    ```

## Adding Custom Server Functions

### Implementing a Skeleton Class

Create a skeleton class that will hold the logic for your completion, diagnostic, and action handlers:

```python

def my_completion_handler(server, params, range, sf):
    # Implement your completion logic here
    pass

def my_diagnostic_handler(server, params, sf):
    # Implement your diagnostic logic here
    pass

def my_action_handler(server, params, range, sf):
    # Implement your action logic here
    pass
```

### Registering Handlers

Register your feature handlers with the `ServerFunctions` instance:

```python
# Instantiate your custom feature class
import custom_features

# Register completion, diagnostic, and action handlers
server_functions.add_completion(custom_features.my_completion_handler)
server_functions.add_diagnostic(custom_features.my_diagnostic_handler)
server_functions.add_action(custom_features.my_action_handler)
```

### Starting the Server

After registering all your handlers, you must start the server functions and then start the language server:

```python
if __name__ == "__main__":
    server_functions.start()
    server.start_io()
```