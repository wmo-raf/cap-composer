window.addEventListener('DOMContentLoaded', (event) => {
    $('.restriction').hide()
    $('.addresses').hide()
    $('.note').hide()
    $('.references').hide()
    $('#id_scope').on('change', function(e) {
        var optionSelected =  $("option:selected", this)
        var valueSelected  = optionSelected.val();
       
        if(valueSelected === 'Restricted'){
            $('.restriction').show()
            $('.addresses').hide()
        } 
        
        if(valueSelected === 'Private'){
            $('.addresses').show()
            $('.restriction').hide()

        }

        if(valueSelected === 'Public'){
            $('.restriction').hide()
            $('.addresses').hide()
        }

    })

    $('.message').on('change', function (e) {
        var optionSelected =  $("option:selected", this)
        var valueSelected  = optionSelected.val();

        if(valueSelected == 'Error'){
            $('.note').show()
        }else if(valueSelected == 'Update'){
            $('.references').show()
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