const vscode = require("vscode")
const net = require('net');
const fs = require('fs');
const { resolve } = require('path');

async function createPipeServer() {

    let workspaceName = await vscode.commands.executeCommand('abbeyai.getWorkspaceName');
    const PIPE_NAME = `\\\\.\\pipe\\${workspaceName.toString()}`;
    const server = net.createServer(async (client) => {
        console.log('Client connected');

        
        let data_result = await new Promise(async (resolve, reject) => { // Wrap the event in a Promise
            client.on('data', async (data) => {
                try {
                    let result = await vscode.commands.executeCommand("abbeyai." + data);
                    resolve(result.toString()); // Resolve the Promise with the result
                    client.write(JSON.stringify(result))

                } catch (error) {
                    console.log(error);
                    reject(error); // Reject the Promise if there is an error
                }
            });
        });

        console.log(data_result)
        
        client.on('end', () => {
            console.log('Client disconnected');

        });
    });

    /*
    // Make sure the pipe doesn't already exist
    try {
        fs.unlinkSync(PIPE_NAME);
    } catch (e) {
        // Ignore if the file does not exist
    }
    */

    server.listen(PIPE_NAME, () => {
        console.log('Server listening on', PIPE_NAME);
    });
}

module.exports = createPipeServer
