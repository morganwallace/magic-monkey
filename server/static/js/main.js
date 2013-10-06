function validate() {

        var letters = /^[A-Za-z]+$/;  
        var shortUrl = $("input[type='text'][name='short-url']").val();
            
        if(shortUrl.length === 0){
            //error
            console.log("please enter something (letters only) for the short url");
            return false;
	}
        else {
            if(shortUrl.match(letters)) {
                //all good
            }
            else{
                //error
                console.log("please enter only letters for the short url");
           	return false;
	     }     
        }
}

$(document).ready(function() {
        $("#url-shorten").submit(validate);
        console.log("ready!");
});
