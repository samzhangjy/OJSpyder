/**
 * OJSpider extension main file
 */
const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const axios = require("axios").default;

var statusBarItem;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	console.log("OJSpider: initializing...");
	console.log("OJSpider: init status bar menu.");
	statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
	statusBarItem.command = "ojspider.login";
	statusBarItem.text = "Login";
	statusBarItem.show();
	context.subscriptions.push(statusBarItem);
	console.log("OJSpider: register command: login.");
	context.subscriptions.push(
		vscode.commands.registerCommand("ojspider.login", () => {
			login();
		})
	);
	console.log("OJSpider: register command: viewProblem.");
	context.subscriptions.push(
		vscode.commands.registerCommand("ojspider.viewProblem", () => {
			// Create and show a new webview
			const panel = vscode.window.createWebviewPanel(
				"ojspider", // Identifies the type of the webview. Used internally
				"OJSpider", // Title of the panel displayed to the user
				vscode.ViewColumn.One, // Editor column to show the new webview panel in.
				{
					// Enable scripts in the webview
					enableScripts: true,
					// No reload when switching between windows
					retainContextWhenHidden: true
				}
			);

			// And set its HTML content
			panel.webview.html = getWebviewContent(context, "./vue/viewProblem/dist/index.html");
		})
	);
	console.log("OJSpider: initialize finished.");
}

/**
 * Login to the OJ
 */
async function login() {
	console.log("OJSpider: logging in...");
	// username and password
	var username = "", password = "";
	// ask for username
	await vscode.window.showInputBox({
		// ignore switching tabs
		ignoreFocusOut: true,
		// placeholder
		placeHolder: "用户名",
		// prompt
		prompt: "请输入OJ用户名"
	}).then((value) => {
		// set username
		username = value
	});
	// ask for password
	await vscode.window.showInputBox({
		ignoreFocusOut: true,
		placeHolder: "密码",
		prompt: "请输入OJ密码",
		// enable password mode (with dots)
		password: true
	}).then((value) => {
		// set password
		password = value
	});
	// send post request to the backend
	await axios.post('http://localhost:5000/api/login', {
		// username
		username: username,
		// password
		password: password
	}).then((data) => {
		const result = data.data;
		// error handling
		// success
		if (result.status === "success") {
			// show success msg
			vscode.window.showInformationMessage('登录OJ成功');
			console.log("OJSpider: login success.");
		}
		// error
		else {
			// show error msg
			vscode.window.showErrorMessage(`登录OJ失败：${result.msg}`);
			console.log("OJSpider: login failed.");
		}
	});

}

/**
 * Get the webview content
 * @param {vscode.ExtensionContext} context 
 * @param {String} uri 
 * @returns {String} the webview content
 */
function getWebviewContent(context, uri) {
	// the root path of the extension
	const rootPath = context.extensionPath;
	// the absolute path of the file
	const abPath = path.join(rootPath, uri);
	// the dir path of the file
	const dirPath = path.dirname(abPath);
	// read the file
	var html = fs.readFileSync(abPath, "utf-8");
	// pre-process the file
	// replace src and href with vscode-resource: ...
	html = html.replace(/src=(.*?)|href=(.*?)/g, function (m, ops, origin) {
		// get path with vscode-resource
		const path =
			`${m}${vscode.Uri.file(dirPath).with({ scheme: "vscode-resource" }).toString()}`
		return path;
	});
	return html;
}
exports.activate = activate;

// this method is called when your extension is deactivated
function deactivate() { }

module.exports = {
	activate,
	deactivate,
};
