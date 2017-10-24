$(document).ready(function(){
    $('#btn_showDesktop').click(function(){
        $('#div_desktop').toggle();
    });

    $('#btn_start').click(function(){
        $.ajax({
            type:'POST',
            url:'/services/startBot',
            data:'',
            success:function(data){
                $('#div_flash').html(data);
            }
        });
    });
});
