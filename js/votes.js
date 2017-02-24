function VoteUp(storyKey){
    $.ajax({
      type: "POST",
      url: "/blog/addwag",
      dataType: 'json',
      data: JSON.stringify({ "storyKey": storyKey})
    })
    .done(function( data ) { // check why I use done
                    $('#wag_at_post'+data['posts']['storyKey']).hide();
                    $('#unwag_post'+data['posts']['storyKey']).css('display','block');
                    if (data['posts']['wags'] == 1) {
                        $('.voteCount'+data['posts']['storyKey']).text(data['posts']['wags'] + " Wag");
                    }
                    else {
                        $('.voteCount'+data['posts']['storyKey']).text(data['posts']['wags'] + " Wags");
                    }
    });
};

function VoteDown(postKey){
    $.ajax({
      type: "POST",
      url: "/blog/removewag",
      dataType: 'json',
      data: JSON.stringify({ "postKey": postKey})
    })
    .done(function( data ) { // check why I use done
                    $('#unwag_post'+data['posts']['postKey']).hide();
                    $('#wag_at_post'+data['posts']['postKey']).css('display','block');
                    if (data['posts']['wags'] == 1) {
                        $('.voteCount'+data['posts']['postKey']).text(data['posts']['wags'] + ' Wag');
                    }
                    else {
                        $('.voteCount'+data['posts']['postKey']).text(data['posts']['wags'] + ' Wags');
                    }
    });
};