$(document).ready(loadNews(1,"",0,"Global"));



function loadNews(page=1, keyword = "",reload=0, cate=""){
     url= "test_get"
     if (keyword == ""){
         if (reload == 1){
            $('#listTitle').text('Global News')
         }
         if (cate != ""){
            $('#listTitle').text(cate+' News')
         }
     }else{
        url= "search_news"
     }

     if (page == 0){
          page =  parseInt(localStorage.getItem('page'))
          page -= 1
     }else if (page == 10){
          page = parseInt(localStorage.getItem('page'))
          page += 1
     }
     console.log(page)
     data = {"page": page, "cate":cate}


     var title = $('#listTitle').html()
     if (keyword!= "" || title.substring(0, 19).indexOf("Search Result") != -1){
        if (keyword == ""){
            keyword = title.substring(20,title.length-1)
        }
        url= "search_news"
        data["keyword"]=  keyword
     }else{
        cate = title.split(' ')[0]
        data["cate"] = cate
     }

     $.ajax({
        url: url,
        type: "get",
        dataType: "text",
        data:data,
        success: function (data) {
            $("#actTable").empty();
            $("#change_page").empty();
            var jsonText = JSON.parse(data);
            var actResult = ""
            var max_page = Math.ceil(parseFloat(jsonText[0])/10)
            change_page = '<li id="pre" onclick="loadNews(0)"><a href="#listTitle">&laquo;</a></li>'
            for (var i =1;i<max_page+1;i++){
                change_page += '<li onclick="loadNews('+i+')"><a id="page_'+i+'" href="#listTitle">'+i+'</a></li>'
            }
            change_page +=  '<li onclick="loadNews(10)" id="next"><a href="#listTitle">&raquo;</a></li>'
            $('#change_page').append(change_page);

            for (var i = 1; i < jsonText.length; i++) {
                var score = Number(jsonText[i].timerank * 100).toFixed(1)
                var date_new = timestampToTime(parseInt(jsonText[i].publish_date)-28800)
                img_url = "abc.png"
                img_ref = "http://www.abc.net.au"
                if (jsonText[i].url.toString().substring(0,20).indexOf("sbs") != -1){
                    img_url = "sbs.png"
                    img_ref = "http://www.sbs.com.au"
                }else if (jsonText[i].url.toString().substring(0,20).indexOf("can") != -1){
                    img_url = "cbt.png"
                    img_ref="http://www.canberratimes.com.au"
                }
                score += "%"
                actResult +=
                '<div  class="list-group-item col-sm-12" style="padding:10px 15px 20px 15px">' +
                '<div">'+
                    '<a href="'+ img_ref +'">'+
                    '<img src="../static/assets/image/'+img_url+'" class="img-responsive" style="float:left;height:18px;padding-top: 2px;"></a>' +
                    '<div href="#" class="timeline-category-name">'+jsonText[i].category+'</div>'+

                    '<div class="starbg"><div style="width: '+score+';"></div></div>' +

                    '<div href="#">'+
                        '<h3 class="timeline-post-title">'+jsonText[i].title+'</h3>'+
                    '</div>'+
                    '<div class="timeline-post-info">'+
                        '<div href="#" class="author">'+jsonText[i].authors+'</div>'+
                        '<div href="#" class="author">'+date_new+'</div>'+
                        '<span class="dot">'+ '<a href="'+jsonText[i].url+'" class="news_url">'+jsonText[i].url+'</a>'+'</span>'+
                    '</div>'+
                    '<img id="'+jsonText[i].news_id+'_d" src="../static/assets/image/d.png" class="img-responsive" onclick="comment(this)" style="float:right;height:20px;padding-top: 2px;">'+
                    '<p id="'+jsonText[i].news_id+'_disapprove_num" style="float:right;">'+jsonText[i].disapprove+'</p>' +
                    '<img id="'+jsonText[i].news_id+'_a" src="../static/assets/image/a.png" class="img-responsive" onclick="comment(this)" style="float:right;height:20px;padding-top: 2px; margin-right:10px">'+
                    '<p id="'+jsonText[i].news_id+'_approve_num" style="float:right;">'+jsonText[i].approve+'</p>' +
                '</div>'+
                '</div>'
            }
            $('#actTable').append(actResult);

            target_page = "page_" + page
            $("#" + target_page + "").css("background", "yellow")
            localStorage.setItem('page',page)
            if (page == max_page){
                $('#next').removeAttr('onclick')
            }
            if (page == 1){
                $('#pre').removeAttr('onclick')
            }
        },
        error: function (data) {
            console.log("no News");
        }
    });
    loadLatestNews()
}

function searchNews(){


    if ($('#searchKeyword').val() == null || $('#searchKeyword').val() == ""){
        alert("no keywords")
    }else {
        var keywords = $('#searchKeyword').val()
        $('#listTitle').text('Search Results for "' + keywords + '"')
        loadNews(1, keywords)
    }
}

function loadMore(){
}
function comment(btn){
    var id_comment = btn.getAttribute('id')
    var id = id_comment.split('_')[0]
    var comment = id_comment.split('_')[1]
    $.ajax({
        url: "comment",
        type: "get",
        dataType: "text",
        data:{"news_id": parseInt(id), "comment_type":comment},
        success: function (data) {
            var jsonText = JSON.parse(data)
            if (jsonText.status == 1){
                var app_num = '#'+id+'_approve_num'
                var disapp_num = '#'+id+'_disapprove_num'
                $(app_num).html(jsonText.approve)
                $(disapp_num).html(jsonText.disapprove)
                alert('commented!')
            }else{
                alert('You have already commented!')
            }

        },
        error: function (data) {
            console.log("service err");
        }
    });
}

function loadLatestNews(){
     $.ajax({
        url: "test_get_latest",
        type: "get",
        dataType: "text",
        success: function (data) {
            $("#acTableLatest").empty();
            var jsonText = JSON.parse(data);
            var actResult = ""
            for (var i = 0; i < jsonText.length; i++) {
                var score = Number(jsonText[i].timerank)
                var date_new = timestampToTime(parseInt(jsonText[i].publish_date)-28800)
                actResult +=
                '<a href="'+jsonText[i].url+'" class="list-group-item col-sm-12">' +
                '<div href="#">'+
                        '<h5 class="timeline-post-title">'+jsonText[i].title+'</h5>'+
                    '</div>'+
                    '<div class="timeline-post-info">'+
                        '<div href="#" style="font-size:12px">Score: '+score+'</div>'+
                        '<div href="#" style="font-size:12px">'+date_new+'</div>'+
                 '</div>'

            }
            $('#acTableLatest').append(actResult);
        },
        error: function (data) {
            console.log("no News");
        }
    });
}


function timestampToTime(timestamp) {
    var date = new Date(timestamp * 1000);
    var Y = date.getFullYear() + '-';
    var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
    var D = date.getDate() + ' ';
    var h = date.getHours() + ':';
    var m = (date.getMinutes() < 10 ? '0'+(date.getMinutes()) : date.getMinutes()) + ':';
    var s =  (date.getSeconds() < 10 ? '0'+(date.getSeconds()) : date.getSeconds())
    return Y+M+D+h+m+s;
}


$('.search-toggle').on('click', function(e){
    e.preventDefault();
    $('.search-bar').toggleClass('active');
});