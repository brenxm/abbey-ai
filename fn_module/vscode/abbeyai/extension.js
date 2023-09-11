// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const pipeServer = require("./pipe_connection")
const vscode = require('vscode');
const dirTree = require("directory-tree")


// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "abbeyai" is now active!');

	// Connect pip server
	pipeServer()

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with  registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = []
	disposable.push(vscode.commands.registerCommand('abbeyai.getFolder', function () {
		let workspaceFolders = vscode.workspace.workspaceFolders;
		if (workspaceFolders && workspaceFolders.length > 0) {
			let folderPath = workspaceFolders[0].uri.fsPath;
			vscode.window.showInformationMessage(folderPath)
			return folderPath
		} else {
			console.log("No workspace folder found!");
		}
	}))

	disposable.push(
		vscode.commands.registerCommand('abbeyai.getItemPath', function (){
			let activeEditor = vscode.window.activeTextEditor;

			if (activeEditor){
				let document = activeEditor.document;
				let filePath = document.uri.fsPath;

				return filePath
			} else {
				console.log('No active file.')
			}
		})
	)

	disposable.push(
		vscode.commands.registerCommand('abbeyai.getHighlightedCode', function(){
			let activeEditor = vscode.window.activeTextEditor;

			if (activeEditor){
				let selection = activeEditor.selection;
				let selectedText = activeEditor.document.getText(selection)

				return selectedText
			} else {
				console.log('No active file')
			}
		})
	)

	disposable.push(
		vscode.commands.registerCommand('abbeyai.getActiveCode', function(){
			let activeEditor = vscode.window.activeTextEditor;

			if (activeEditor){
				let document = activeEditor.document;
				let entireFileText = document.getText();

				return entireFileText
			} else {
				console.log('No active file')
			}
		})
	)

	disposable.push(
		vscode.commands.registerCommand('abbeyai.getWorkspaceName', function(){
			let workspaceName;

			if (vscode.workspace.workspaceFolders){
				workspaceName = vscode.workspace.workspaceFolders[0].name;
			}

			return workspaceName
		})
	)

	disposable.push(
		vscode.commands.registerCommand('abbeyai.getData', function(){
			let object = {
				activeCode: "",
				highlightedCode: "",
				folderPath: "",
				folderStructure: "",
				filePath: ""
			}
			

			let workspaceFolders = vscode.workspace.workspaceFolders;
			if (workspaceFolders && workspaceFolders.length > 0) {
				let folderPath = workspaceFolders[0].uri.fsPath;
				vscode.window.showInformationMessage(folderPath)
				object.folderPath = folderPath
			} else {
				console.log("No workspace folder found!");
			}

		
			let activeEditor = vscode.window.activeTextEditor;

			if (activeEditor) {
				let document = activeEditor.document;
				let entireFileText = document.getText();
				let selection = activeEditor.selection;
				let selectedText = activeEditor.document.getText(selection)
				let filePath = document.uri.fsPath;

				object.highlightedCodeStartLine = selection.start.line
				object.highlightedCodeEndLine = selection.end.line
				object.activeCode = entireFileText
				object.highlightedCode = selectedText
				object.filePath = filePath
				let tree = dirTree(object.folderPath, {exclude: [/.vscode$/, /__pycache__/, /.pytest_cache/, /node_modules/, /test/, /utils/, /.git/, /.svn/, /.hg/, /CVS/, /.DS_Store/, /Thumbs.db/]})

				object.folderStructure = visualizeTree(tree)

			} else {
				console.log('no active editor')
			}

			return object
		})
	)

	for(let i = 0; i < disposable.length; i++){
		context.subscriptions.push(disposable[i]);
	}
}


function visualizeTree(tree, prefix = '') {
	let result = prefix + tree.name + '/\n';
	if (tree.children) {
		const len = tree.children.length;
		tree.children.forEach((child, i) => {
			const connector = i < len - 1 ? '├── ' : '└── ';
			const nextPrefix = prefix + (i < len - 1 ? '│   ' : '    ');
			result += prefix + connector + visualizeTree(child, nextPrefix);
		});
	}
	return result;
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
