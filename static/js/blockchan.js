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
