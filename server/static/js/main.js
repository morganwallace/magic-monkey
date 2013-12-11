

function validate() {

		//initialize without errors
		var error=false;

        var letters = /^[A-Za-z]+$/;  
        
        var longurl = $("input[name='long-url']").val();
        var shorturl = $("input[name=short-url]").val();
       
        if (shorturl.match(letters)) {
        //all good
        $("#short-url").parent().removeClass('has-error alert alert-danger');
        }
        else{
			console.log("please enter something (letters only) for the short url");
            $("#short-url").parent().addClass('has-error alert alert-danger');
        	error=true;
        }
            
        if(longurl.length === 0){
            //error
/*             alert("la") */
            console.log("Full URL must not be empty");
            $("#long-url").parent().addClass('has-error alert alert-danger');
            error=true;
		}
		else{
			//good - long url has more than 0 chars
			$("#long-url").parent().removeClass('has-error alert alert-danger');
		}


        if (error == true){
	        return false
        }
        
}

function validate_password(){
	alert(len($("input[name=password").val()));
/*
	if (len($("input[name=password").val())<6){
		alert("your password is too short")
		return false
	}
*/
	return false
}

//automatically create a shortened version of the url
function makeshort(){
/* 	var pathname = window.location.pathname; */
	shorturl_rand=makeid()
	$("input[name='short-url']").val(shorturl_rand)
	return shorturl_rand
	
}

function makeid()
{
    var text = "";
    var possible = "abcdefghijklmnopqrstuvwxyz";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}

function geturl(){
	var path=$(location).attr('href');
/* 	alert(path) */
	path=path.substring(0,path.indexOf("server")+7)+"short/"
	$("#cur_path").html(path);
}

$(document).ready(function() {
		$("#login").submit(validate_password);
        $("#url-shorten").submit(validate);
        $("#short-url").val(makeshort)
        console.log("ready!");
        geturl();
});
