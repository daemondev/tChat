var ChatContainer = React.createClass({
    getInitialState: function(){
        return {
            myProps: {}
            , data:[]
            , ws : null
            , domain : ""
            , separator : "://"
            , port : ""
            , protocol : "ws" + "://"
            , namespace : "/websocket"
        };
    },
    onMessage: function(e){
        var data = eval('(' + e.data + ')');
        this.on(data["event"], data["data"]);
    },
    on: function(event, data){
        if (event == "new chat"){
            var chatList = document.getElementById("txtChatHistory");
            var messageBox = document.getElementById("txtMessage");
            messageBox.value = "";
            chatList.innerHTML = "<li class='collection-item'>" + data.name + " - " + data.message + "</li><hr />" + chatList.innerHTML;
        }
    },
    emit: function (message, data ){
        var json = JSON.stringify({0:message, 1: data})
        this.state.ws.send(json);
    },
    componentWillMount: function(){
        var ws = new WebSocket("wss" + this.state.separator + document.domain + this.state.port + this.state.namespace);
        ws.onmessage = this.onMessage;
        this.setState({ws:ws});
    },
    componentDidMount: function(){
        var user = document.getElementById("lbl_linea").innerHTML;
        var state = Object.assign({}, this.state);
        state.myProps["user"] = user;
        this.setState(state);
    },
    sendMessage: function(event){
        if(event.key == "Enter"){
            var name = this.state.myProps["user"];
            var message = event.target.value;

            var obj = {"name":name, "message": message};
            this.emit("new message", obj);
        }
    },
    render: function(){
        return (
            <div id="divChatContainner" className="chatContainner">

                <div className="chatHistory">
                    <ul id="txtChatHistory">
                    </ul>
                </div>
                <div className="chatMessage">
                    <input type="text" id="txtMessage" placeholder="Enter message" onKeyPress={ this.sendMessage } />
                    <input type="button" value="SEND" id="btnSendMessage" onClick={ this.sendMessage } />
                </div>
            </div>
        )
    }
});

ReactDOM.render(
    <ChatContainer />,
    document.getElementById('divChatWrapper')
);
