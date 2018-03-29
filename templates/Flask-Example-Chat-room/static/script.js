var timeoutID;
var timeout = 1000; // 1 second polling time

function setup() {
	document.getElementById("theButton").addEventListener("click", makePost, true);

	timeoutID = window.setTimeout(poller, timeout);
}

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Error :( Cannot create an XMLHTTP instance');
		return false;
	}

	var msg = document.getElementById("message").value

	httpRequest.onreadystatechange = function() { handlePost(httpRequest, msg) };
	
	httpRequest.open("POST", "/new_msg");
	httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

	var data;
	data = "text=" + msg;
	
	httpRequest.send(data);
}

function handlePost(httpRequest, msg) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			clearInput();
		} else if (httpRequest.status === 301){
			var data = JSON.parse(httpRequest.responseText);
			window.location.replace(data.url);			
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("GET", "/get_messages");
	httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			
			var rows = JSON.parse(httpRequest.responseText);
			for (var i = 0; i < rows.length; i++) {
				addRow(rows[i]);
			}
			
			timeoutID = window.setTimeout(poller, timeout);
			
		} 
		else if (httpRequest.status === 301){
			var data = JSON.parse(httpRequest.responseText);
			window.location.replace(data.url);			
		} else {
			alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
		}
	}
}

function clearInput() {
	document.getElementById("message").value = "";
}

function addRow(message) {
	
	var listRef = document.getElementById("msgList");
	var newLine = document.createElement('li');
	var name_node = document.createTextNode(message.author);
	var text_node = document.createTextNode(message.text);
	var time_node = document.createElement('small');
	var br_node = document.createElement('br');

	time_node.innerHTML = "&mdash; " + message.pub_date;
	
	newLine.appendChild(name_node);
	newLine.appendChild(time_node);
	newLine.appendChild(br_node);
	newLine.appendChild(text_node);
	listRef.appendChild(newLine);	
}

window.addEventListener("load", setup, true);
