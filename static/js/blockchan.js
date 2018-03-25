$(document).ready(function(){
var tpm_open = 0
	$("#topmenubutton").click(function(){
		if(th_open == 0){
			th_open = 1
			$("#topmenu").show();
			$("#topmenuimage").rotate({animateTo:180})

		}
		else{
			th_open = 0
			$("#topmenu").hide();
			$("#topmenuimage").rotate({animateTo:0})
		}
	});

	var th_open = 0
	$("#snth").click(function(){
			if(th_open == 0){
				th_open = 1
				$("#snth").attr('class', 'btn btn-danger');
				$("#snth").html('<span class="glyphicon glyphicon-remove"></span> Close');
				$("#new_post").show();
			}
			else{
				th_open = 0
				$("#snth").attr('class', 'btn');
				$("#new_post").hide();
				if(thread_open === 1){
					$("#snth").html('<span class="glyphicon glyphicon-comment"></span> Reply');
			 }
			 else{
				 $("#snth").html('<span class="glyphicon glyphicon-pencil"></span> Start New Thread');
			 }
			}
	});

 $("#form").submit(function(){
	 th_open = 0
	 $("#snth").attr('class', 'btn');
	 $("#new_post").hide();
	 if(thread_open === 1){
		 $("#snth").html('<span class="glyphicon glyphicon-comment"></span> Reply');
	}
	else{
		$("#snth").html('<span class="glyphicon glyphicon-pencil"></span> Start New Thread');
	}
});

});



var thread_open
	function render_posts(j_text){
	  thread_open = 0
		$("#posts").html("");
		data = JSON.parse(j_text);
		$("#snth").html('<span class="glyphicon glyphicon-pencil"></span> Start New Thread');
		if(data.lenght != 0)
		for(var post in data){
			console.log(data[post])
			author = data[post].author_name
			timestamp = data[post].timestamp;
			post_id = data[post].post_id;
			subject = data[post].subject;
			img_blob = data[post].image;
			comm_count = data[post].comm_count;
			if(comm_count != 0){
				comm_count = '<div style="float:right;">'+comm_count+' comments</div>';
			}
			else{
				comm_count = ''
			}
			if(img_blob == 0){
				image_present = 'style="display:none;"'
			}
			else{
				image_present = ''
			}
			text = data[post].comment;
			pid = "'"+post_id+"'";
	document.getElementById("posts").innerHTML = document.getElementById("posts").innerHTML +
	    '<div class="container">'+
			'<div class="card">'+
			'<div class="card-header"><a style="color:green">'+author+'</a> &nbsp&nbsp&nbsp Timestamp: '+timestamp+' &nbsp&nbsp&nbsp Subject: '+subject+' &nbsp&nbsp&nbsp ID:'+post_id+'</div>'+
			'<div class="card-body"><img '+image_present+' id="image" src="data:image/png;base64, '+img_blob+' width="128" height="128" /> &nbsp '+text+'</div>'+
			'<div class="card-footer">'+comm_count+'<a href="javascript:BackEnd.open_post('+pid+')"><button class="btn btn-sm">View thread</button></a></div>'+
			'</div></div><br>';
			}
	}

	function open_post(j_text){
		data = JSON.parse(j_text);
		console.log(data)
		thread_open = 1
		$("#snth").html('<span class="glyphicon glyphicon-comment"></span> Reply')
		author = data.author_name;
		timestamp = data.timestamp;
		post_id = data.post_id
		subject = data.subject
		img_blob = data.image
		if(img_blob == 0){
			image_present = 'style="display:none;"'
		}
		else{
			image_present = ''
		}
		document.getElementById("posts").innerHTML = '';
		document.getElementById("posts").innerHTML = document.getElementById("posts").innerHTML +
		    '<input type="text" form="form" name="thread" value="'+post_id+'" style="display:none;">'+
		    '<div class="container">'+
				'<div class="card">'+
				'<div class="card-header bg-dark text-white"><a style="color:green">'+author+'</a> Timestamp: '+timestamp+' &nbsp&nbsp&nbsp Subject: '+subject+' &nbsp&nbsp&nbsp ID:'+post_id+'</div>'+
				'<div class="card-body" align="center"><img '+image_present+' id="image" src="data:image/png;base64, '+img_blob+' width="512" height="256" /> <br> '+text+'</div>'+
				'</div></div><br>';
		for(post in data.comments){
			author = data.comments[post].author_name
			timestamp = data.comments[post].timestamp;
			post_id = data.comments[post].post_id;
			subject = data.comments[post].subject;
			img_blob = data.comments[post].image;
			if(img_blob == 0){
				image_present = 'style="display:none;"'
			}
			else{
				image_present = ''
			}
			text = data.comments[post].comment;
			document.getElementById("posts").innerHTML = document.getElementById("posts").innerHTML +
					'<div class="container">'+
					'<div class="card">'+
					'<div class="card-header"><a style="color:green">'+author+'</a> &nbsp&nbsp&nbsp Timestamp: '+timestamp+' &nbsp&nbsp&nbsp Subject: '+subject+' &nbsp&nbsp&nbsp ID:'+post_id+'</div>'+
					'<div class="card-body"><img '+image_present+' id="image" src="data:image/png;base64, '+img_blob+' width="128" height="128" /> &nbsp '+text+'</div>'+
					'</div></div><br>';
		}
	}
