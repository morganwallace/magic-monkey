function validate() {


        var longurl = $("input[name='long-url']").val();
        
            
        if(longurl.length === 0){
            //error
/*             alert("la") */
            console.log("please enter something (letters only) for the short url");
            $("#long-url").parent().toggleClass('has-error');
            return false;
	}
        else {
            if(longurl.match(letters)) {
                //all good
            }
            else{
                //error
                console.log("please enter only letters for the short url");
           	return false;
	     }     
        }
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
        $("#url-shorten").submit(validate);
        $("#short-url").val(makeshort)
        console.log("ready!");
        geturl();
});
