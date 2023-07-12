
window.addEventListener('DOMContentLoaded', (event) => {
    // console.log("scope value",$('#id_scope').val())

    // check scope 
    if($('#id_scope').val() === 'Restricted'){
        $('.restriction').show()
        $('.addresses').hide()
    } 
    
    if($('#id_scope').val() === 'Private'){
        $('.addresses').show()
        $('.restriction').hide()

    }

    if($('#id_scope').val() === 'Public'){
        $('.restriction').hide()
        $('.addresses').hide()
    }
    
    // check message 
    if($('#id_message_type').val() === 'Error'){
        $('.note').show()
        $('.references').show()
    }else if($('#id_message_type').val()  === 'Update' || $('#id_message_type').val()  === 'Cancel' || $('#id_message_type').val()  === 'Ack'){
        $('.references').show()
        $('.note').hide()

    }else{
        $('.note').hide()
        $('.references').hide()
    }

    $('#id_scope').on('change', function(e) {
        var optionSelected =  $("option:selected", this)
        var valueSelected  = optionSelected.val();
       
        if(valueSelected === 'Restricted'){
            $('.restriction').show()
            $('.addresses').hide()
        } 
        
        if(valueSelected === 'Private'){
            $('.addresses').show()
            // $('#id_restriction').html('')
            $('.restriction').hide()

        }

        if(valueSelected === 'Public'){
            $('.restriction').hide()
            // $('#id_restriction').html('')
            $('.addresses').hide()
        }

    })

    $('.message').on('change', function (e) {
        var optionSelected =  $("option:selected", this)
        var valueSelected  = optionSelected.val();

        if(valueSelected == 'Error'){
            $('.note').show()
            $('.references').show()
        }else if(valueSelected == 'Update' || valueSelected == 'Cancel' || valueSelected == 'Ack'){
            $('.references').show()
            $('.note').hide()
        }else{
            $('.note').hide()
            $('.references').hide()
        }

        
        
    })


})



// django.jQuery(document).ready(function(){


    // if (django.jQuery('#id_scope').is(':checked')) {
    //     django.jQuery(".page").hide();
    //     hide_page=true;
    // } else {
    //     django.jQuery(".page").show();
    //     hide_page=false;
    // }
    // django.jQuery("#id_has_submenu").click(function(){
    //     hide_page=!hide_page;
    //     if (hide_page) {
    //         django.jQuery(".page").hide();
    //     } else {
    //         django.jQuery(".page").show();
    //     }
    // })
// })