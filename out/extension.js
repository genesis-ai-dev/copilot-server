/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: // www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------- */
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const net = require("net");
const path = require("path");
const vscode = require("vscode");
const semver = require("semver");
const python_extension_1 = require("@vscode/python-extension");
const node_1 = require("vscode-languageclient/node");
const MIN_PYTHON = semver.parse("3.7.9");
// Some other nice to haves.
// TODO: Check selected env satisfies pygls' requirements - if not offer to run the select env command.
// TODO: TCP Transport
// TODO: WS Transport
// TODO: Web Extension support (requires WASM-WASI!)
let client;
let clientStarting = false;
let python;
let logger;
/**
 * This is the main entry point.
 * Called when vscode first activates the extension
 */
async function activate(context) {
    logger = vscode.window.createOutputChannel('pygls', { log: true });
    logger.info("Extension activated.");
    await getPythonExtension();
    if (!python) {
        return;
    }
    // Restart language server command
    context.subscriptions.push(vscode.commands.registerCommand("pygls.server.restart", async () => {
        logger.info('restarting server...');
        await startLangServer();
    }));
    // Execute command... command
    context.subscriptions.push(vscode.commands.registerCommand("pygls.server.executeCommand", async () => {
        await executeServerCommand();
    }));
    // Restart the language server if the user switches Python envs...
    context.subscriptions.push(python.environments.onDidChangeActiveEnvironmentPath(async () => {
        logger.info('python env modified, restarting server...');
        await startLangServer();
    }));
    // ... or if they change a relevant config option
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(async (event) => {
        if (event.affectsConfiguration("pygls.server") || event.affectsConfiguration("pygls.client")) {
            logger.info('config modified, restarting server...');
            await startLangServer();
        }
    }));
    // Start the language server once the user opens the first text document...
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(async () => {
        if (!client) {
            await startLangServer();
        }
    }));
    // ...or notebook.
    context.subscriptions.push(vscode.workspace.onDidOpenNotebookDocument(async () => {
        if (!client) {
            await startLangServer();
        }
    }));
    // Restart the server if the user modifies it.
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(async (document) => {
        const expectedUri = vscode.Uri.file(path.join(getCwd(), getServerPath()));
        if (expectedUri.toString() === document.uri.toString()) {
            logger.info('server modified, restarting...');
            await startLangServer();
        }
    }));
}
exports.activate = activate;
function deactivate() {
    return stopLangServer();
}
exports.deactivate = deactivate;
/**
 * Start (or restart) the language server.
 *
 * @param command The executable to run
 * @param args Arguments to pass to the executable
 * @param cwd The working directory in which to run the executable
 * @returns
 */
async function startLangServer() {
    // Don't interfere if we are already in the process of launching the server.
    if (clientStarting) {
        return;
    }
    clientStarting = true;
    if (client) {
        await stopLangServer();
    }
    const config = vscode.workspace.getConfiguration("pygls.server");
    const cwd = getCwd();
    const serverPath = getServerPath();
    logger.info(`cwd: '${cwd}'`);
    logger.info(`server: '${serverPath}'`);
    const resource = vscode.Uri.joinPath(vscode.Uri.file(cwd), serverPath);
    const pythonCommand = await getPythonCommand(resource);
    if (!pythonCommand) {
        clientStarting = false;
        return;
    }
    logger.debug(`python: ${pythonCommand.join(" ")}`);
    const serverOptions = {
        command: pythonCommand[0],
        args: [...pythonCommand.slice(1), serverPath],
        options: { cwd },
    };
    client = new node_1.LanguageClient('pygls', serverOptions, getClientOptions());
    const promises = [client.start()];
    if (config.get("debug")) {
        promises.push(startDebugging());
    }
    const results = await Promise.allSettled(promises);
    clientStarting = false;
    for (const result of results) {
        if (result.status === "rejected") {
            logger.error(`There was a error starting the server: ${result.reason}`);
        }
    }
}
async function stopLangServer() {
    if (!client) {
        return;
    }
    if (client.state === node_1.State.Running) {
        await client.stop();
    }
    client.dispose();
    client = undefined;
}
function startDebugging() {
    if (!vscode.workspace.workspaceFolders) {
        logger.error("Unable to start debugging, there is no workspace.");
        return Promise.reject("Unable to start debugging, there is no workspace.");
    }
    // TODO: Is there a more reliable way to ensure the debug adapter is ready?
    setTimeout(async () => {
        await vscode.debug.startDebugging(vscode.workspace.workspaceFolders[0], "pygls: Debug Server");
    }, 2000);
}
function getClientOptions() {
    const config = vscode.workspace.getConfiguration('pygls.client');
    const options = {
        documentSelector: config.get('documentSelector'),
        outputChannel: logger,
        connectionOptions: {
            maxRestartCount: 0 // don't restart on server failure.
        },
    };
    logger.info(`client options: ${JSON.stringify(options, undefined, 2)}`);
    return options;
}
function startLangServerTCP(addr) {
    const serverOptions = () => {
        return new Promise((resolve /*, reject */) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(addr, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };
    return new node_1.LanguageClient(`tcp lang server (port ${addr})`, serverOptions, getClientOptions());
}
/**
 * Execute a command provided by the language server.
 */
async function executeServerCommand() {
    var _a;
    if (!client || client.state !== node_1.State.Running) {
        await vscode.window.showErrorMessage("There is no language server running.");
        return;
    }
    const knownCommands = (_a = client.initializeResult.capabilities.executeCommandProvider) === null || _a === void 0 ? void 0 : _a.commands;
    if (!knownCommands || knownCommands.length === 0) {
        const info = client.initializeResult.serverInfo;
        const name = (info === null || info === void 0 ? void 0 : info.name) || "Server";
        const version = (info === null || info === void 0 ? void 0 : info.version) || "";
        await vscode.window.showInformationMessage(`${name} ${version} does not implement any commands.`);
        return;
    }
    const commandName = await vscode.window.showQuickPick(knownCommands, { canPickMany: false });
    if (!commandName) {
        return;
    }
    logger.info(`executing command: '${commandName}'`);
    const result = await vscode.commands.executeCommand(commandName /* if your command accepts arguments you can pass them here */);
    logger.info(`${commandName} result: ${JSON.stringify(result, undefined, 2)}`);
}
/**
 * If the user has explicitly provided a src directory use that.
 * Otherwise, fallback to the examples/servers directory.
 *
 * @returns The working directory from which to launch the server
 */
function getCwd() {
    const config = vscode.workspace.getConfiguration("pygls.server");
    const cwd = config.get('cwd');
    if (cwd) {
        return cwd;
    }
    const serverDir = path.resolve(path.join(__dirname, "..", "..", "servers"));
    return serverDir;
}
/**
 *
 * @returns The python script that implements the server.
 */
function getServerPath() {
    const config = vscode.workspace.getConfiguration("pygls.server");
    const server = config.get('launchScript');
    return server;
}
/**
 * Return the python command to use when starting the server.
 *
 * If debugging is enabled, this will also included the arguments to required
 * to wrap the server in a debug adapter.
 *
 * @returns The full python command needed in order to start the server.
 */
async function getPythonCommand(resource) {
    const config = vscode.workspace.getConfiguration("pygls.server", resource);
    const pythonPath = await getPythonInterpreter(resource);
    if (!pythonPath) {
        return;
    }
    const command = [pythonPath];
    const enableDebugger = config.get('debug');
    if (!enableDebugger) {
        return command;
    }
    const debugHost = config.get('debugHost');
    const debugPort = config.get('debugPort');
    try {
        const debugArgs = await python.debug.getRemoteLauncherCommand(debugHost, debugPort, true);
        // Debugpy recommends we disable frozen modules
        command.push("-Xfrozen_modules=off", ...debugArgs);
    }
    catch (err) {
        logger.error(`Unable to get debugger command: ${err}`);
        logger.error("Debugger will not be available.");
    }
    return command;
}
/**
 * Return the python interpreter to use when starting the server.
 *
 * This uses the official python extension to grab the user's currently
 * configured environment.
 *
 * @returns The python interpreter to use to launch the server
 */
async function getPythonInterpreter(resource) {
    const config = vscode.workspace.getConfiguration("pygls.server", resource);
    const pythonPath = config.get('pythonPath');
    if (pythonPath) {
        logger.info(`Using user configured python environment: '${pythonPath}'`);
        return pythonPath;
    }
    if (!python) {
        return;
    }
    if (resource) {
        logger.info(`Looking for environment in which to execute: '${resource.toString()}'`);
    }
    // Use whichever python interpreter the user has configured.
    const activeEnvPath = python.environments.getActiveEnvironmentPath(resource);
    logger.info(`Found environment: ${activeEnvPath.id}: ${activeEnvPath.path}`);
    const activeEnv = await python.environments.resolveEnvironment(activeEnvPath);
    if (!activeEnv) {
        logger.error(`Unable to resolve envrionment: ${activeEnvPath}`);
        return;
    }
    const v = activeEnv.version;
    const pythonVersion = semver.parse(`${v.major}.${v.minor}.${v.micro}`);
    // Check to see if the environment satisfies the min Python version.
    if (semver.lt(pythonVersion, MIN_PYTHON)) {
        const message = [
            `Your currently configured environment provides Python v${pythonVersion} `,
            `but pygls requires v${MIN_PYTHON}.\n\nPlease choose another environment.`
        ].join('');
        const response = await vscode.window.showErrorMessage(message, "Change Environment");
        if (!response) {
            return;
        }
        else {
            await vscode.commands.executeCommand('python.setInterpreter');
            return;
        }
    }
    const pythonUri = activeEnv.executable.uri;
    if (!pythonUri) {
        logger.error(`URI of Python executable is undefined!`);
        return;
    }
    return pythonUri.fsPath;
}
async function getPythonExtension() {
    try {
        python = await python_extension_1.PythonExtension.api();
    }
    catch (err) {
        logger.error(`Unable to load python extension: ${err}`);
    }
}
//# sourceMappingURL=extension.js.map