import json
import logging

from pygls.server import LanguageServer
from tools.ls_tools import ServerFunctions

logger = logging.getLogger(__name__)

class ExtendedLanguageServer(LanguageServer):
    def __init__(self, name, version, **kwargs):
        super().__init__(name, version)
        self.metadata = {}
        
def get_project_metadata(params, server: ExtendedLanguageServer, sf: ServerFunctions):
    # NOTE: scripture burrito uses a metadata.json file to store metadata about the project that we need to expose to the client.
    sf.server.metadata = json.loads(server.workspace.root_path + "/metadata.json")
    logger.warning(f"Metadata: {sf.server.metadata}")