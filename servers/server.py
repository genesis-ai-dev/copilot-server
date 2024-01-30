import subprocess
import os

from extended_language_server import ExtendedLanguageServer, get_project_metadata
from tools.ls_tools import ServerFunctions
from servable.spelling import ServableSpelling
from servable.servable_wb import wb_line_diagnostic
from servable.servable_embedding import ServableEmbedding
# try:
# except ImportError:

#     script_directory = os.path.dirname(os.path.abspath(__file__))
#     requirements_file = os.path.join(script_directory, "requirements.txt")
#     subprocess.check_call(["pip", "install", "--break-system-packages", "-r", requirements_file, "-qq"])
    
    # exit()
  

server = ExtendedLanguageServer("code-action-server", "v0.1") # TODO: #1 Dynamically populate metadata from package.json?

server_functions = ServerFunctions(server=server, data_path='/')
spelling = ServableSpelling(sf=server_functions, relative_checking=True)
embedding = ServableEmbedding(sf=server_functions)

server_functions.add_completion(spelling.spell_completion)
server_functions.add_completion(embedding.embed_completion)

server_functions.add_diagnostic(spelling.spell_diagnostic)
server_functions.add_diagnostic(wb_line_diagnostic)
server_functions.add_action(spelling.spell_action)
server_functions.add_initialize_function(get_project_metadata)

def add_dictionary(args):
    return spelling.add_dictionary(args)

server.command("pygls.server.add_dictionary")(add_dictionary)

if __name__ == "__main__":
    print('running:')
    server_functions.start()
    server.start_io()