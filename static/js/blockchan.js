var th_open = 0
function new_thread(){
	if(th_open == 0){
		th_open = 1
		document.getElementById("snth").innerHTML = '[<span class="glyphicon glyphicon-remove"></span>Close]';
		document.getElementById("new_post").style.display = "block";
	}
	else{
		th_open = 0
		document.getElementById("snth").innerHTML = '[<span class="glyphicon glyphicon-pencil"></span> Start New Thread]';
		document.getElementById("new_post").style.display = "none";
	}
}
function render_post(j_text){
	data = JSON.parse(j_text);
	document.getElementById("posts").innerHTML = ''
	for(var post in data){
		timestamp = data[post].timestamp;
		post_id = data[post].post_id;
		subject = data[post].subject;
		img_blob = data[post].image;
		text = data[post].comment;
		document.getElementById("posts").innerHTML = document.getElementById("posts").innerHTML +"<br>"+'</left><div class="container"><div class="panel panel-default"><div class="panel-heading"><a style="color:green">Anonymous</a> &nbsp&nbsp&nbsp Timestamp: '+timestamp+' &nbsp&nbsp&nbsp ID:'+post_id+'</div><div class="panel-body"><a href="javascript:big_image('+post_id+')"><img id="'+post_id+'"src="data:image/png;base64, '+img_blob+' height="200px" width="200px" border="1px"/></a>&nbsp'+text+'</div><div class="panel-footer"><right><a href="javascript:open_thread('+post_id+')" class="btn btn-default">View thread</a></right></div></div></div></left>'

		}
}

var menu_open = 0
function s_menu(){
	if(menu_open == 0){
		document.getElementById("post_search").style.display = 'block';
		document.getElementById("s_bar").innerHTML = '&nbsp;[<span class="glyphicon glyphicon-remove"></span>Close]';
		menu_open = 1
	}
	else{
		document.getElementById("post_search").style.display = 'none';
		document.getElementById("s_bar").innerHTML = '&nbsp;[<span class="glyphicon glyphicon-search"></span>Search]';
		menu_open = 0
	}
}

function open_thread(pid){
	document.getElementById("posts").innerHTML = ''
}
