$(document).ready(function() {
    $("#actors-list").change(function(){
        console.log("whatata");
        var selected_actors = $(this).val();
        var form_container = $("#characters-container");
        if(selected_actors){
            form_container.empty();
            $.each(selected_actors, function(index, actor){
                var actor_name = actor.split(',')[1].slice(2,-2)
                var actor_id = actor.split(',')[0].slice(2,-1)
                form_container.append('<label for="string-input">'+actor_name+' (nazwa postaci)</label><br><input type="text" id="string-input" name="actor_'+index+'"><input type="hidden" name="actor_'+index+'_h" value="'+actor_id+'"><br><br>');
                // name = "actor_<nr-of-string-field>"
                // value of hidden is actor_id
            });
            $(".submit-button").on("click", function(event) {
                if($("input[name^='actor_']").filter(":visible").toArray().some(elem => !elem.value)){
                    event.preventDefault();
                    alert("Należy podać nazwę postaci!");
                }
            });
        }else{
            form_container.empty();
        }
    });
});


