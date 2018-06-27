from model import entities
from server_handling import format_to_file_name

def create_ajax_html(show):
    name =    show.name+".html"
    name = format_to_file_name(name)
    f = open("templates/shows/"+name,"w+")
    f.write(html_string_first)
    f.close()
    f = open("templates/shows/" + name, "a")
    f.write(show.name + html_ajax_string_after_title + format_to_file_name(show.name)+html_ajax_string_after_var)
    f.close()
    return None

def create_html(show):
    name = show.name + ".html"
    name = format_to_file_name(name)
    f = open("templates/shows/" + name, "w+")
    f.write(html_string_first)
    f.close()
    f = open("templates/shows/" + name, "a")
    f.write(show.name + html_string_afterTitle+show.name+html_string_afterHeader + \
            show.imageurl + html_string_afterImage + show.description+\
            html_string_afterDescription+show.seasons+html_string_afterSeasons+show.episodes+html_string_afterEpisodes+\
            show.rank+html_string_afterRank+show.rating+html_string_afterRating+show.name+html_string_last)
    f.close()
    return None

def create_ranking(n,session,):
    f = open("templates/ranking.html","w+")
    f.write(ranking_string_first)
    f.close()
    f = open("templates/ranking.html", "a")
    for i in range(1,n+1):
        show = session.query(entities.Show).filter(entities.Show.rank == str(i)).first()
        f.write(create_single_ranking(show))
    f.write(ranking_string_last)
    f.close()
    return None

def create_single_ranking(show):
    string="<h2>"+show.rank+". "+show.name+" (rating:"+show.rating+")</h2>"
    return string

html_string_first = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>"""

html_string_afterTitle ="""
</title>
	<link rel="stylesheet" href="{{url_for('static',filename='styles/show_style.css')}}">
	<link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
</head>
<body>
	<h1 style="color:#ffffff">
"""

html_string_afterHeader = """
	</h1>
	<div class="imag">
		<img src="
"""

html_string_afterImage = """
		" alt="Image" width="450" height="400"/>
	</div>
	<div class="texto">
		<p style="color:#ffffff">
"""

html_string_afterDescription="""
		</p>

		<div class="ep" style="color: #ffffff">
			<h3>Seasons</h3>
			<p>
"""

html_string_afterSeasons="""
			</p>
			<h3>Episodes</h3>
			<p>
"""

html_string_afterEpisodes="""
            </p>
			<h3>Rank</h3>
			<p>
"""

html_string_afterRank="""
            </p>
			<h3>Rating</h3>
			<p>
"""


html_string_afterRating="""
			</p>
		</div>
		<h3 style="color: #ffffff">Rate</h3>	
	</div>
	<form action=/add method="post">
	<div class="rating">
		<input type="radio" name="star" value="5"  id="star1"><label for="star1">
		</label>
		<input type="radio" name="star" value="4"  id="star2"><label for="star2">
		</label>	
		<input type="radio" name="star" value="3"  id="star3"><label for="star3">
		</label>
		<input type="radio" name="star" value="2"  id="star4"><label for="star4">
		</label>
		<input type="radio" name="star" value="1" id="star5"><label for="star5">
		</label>
	</div>
	<input type="text" name="showName" value="
"""

html_string_last = """
" style="margin-left: 5%" readonly>
	<button style = "float:right;margin-right:5%" type="submit">Send</button>
	</form>
</body>
</html>
"""


ranking_string_first = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Ranking</title>
	<link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
</head>
<body style="background:black;color:white">
<h1>Ranking:</h1>
"""

ranking_string_last = """
</body>
</html>
"""

html_ajax_string_first = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>
"""

html_ajax_string_after_title = """
</title>
	<link rel="stylesheet" href="{{url_for('static',filename='styles/show_style.css')}}">
	<link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
</head>
<body style="padding-left:20px">
    <div class = "insertWithJS">

    </div>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script>
    var showName = '"""

html_ajax_string_after_var="""';
$.getJSON("/json/"+showName, function(data){
         var items = []
         i = 0
         $.each(data, function(){

              f = '<h1 style="color:#ffffff">'+data[i]['name']+'</h1>';

              f = f+'<div class="imag">';
                  f = f+'<img src="' + data[i]['imageurl']+'" alt="Image" width="450" height="400"/>';
              f = f+'</div>';

              f = f+'<div class="texto">';
                  f = f+'<p style="color:#ffffff">'+data[i]['description']+'</p>';
                  f = f+'<div class="ep" style="color: #ffffff">';
                      f = f+'<h3>Seasons</h3>';
                          f = f+'<p>'+data[i]['seasons']+'</p>';
                      f = f+'<h3>Episodes</h3>'
                          f = f+'<p>'+data[i]['episodes']+'</p>';
                      f = f+'<h3>Rank</h3>';
                          f = f+'<p>'+data[i]['rank']+'</p>';
                      f = f+'<h3>Rating</h3>';
                          f = f+'<p>'+data[i]['rating']+'</p>';
                  f = f+'</div>';

                  f = f+'<h3 style="color: #ffffff">Rate</h3>';
              f = f+' </div>';

              f = f+'<form action=/add method="post">';
              f = f+'<div class="rating">';
                  f = f+'<input type="radio" name="star" value="5"  id="star1"><label for="star1"></label>';
                  f = f+'<input type="radio" name="star" value="4"  id="star2"><label for="star2"></label>';
                  f = f+'<input type="radio" name="star" value="3"  id="star3"><label for="star3"></label>';
                  f = f+'<input type="radio" name="star" value="2"  id="star4"><label for="star4"></label>';
                  f = f+'<input type="radio" name="star" value="1"  id="star5"><label for="star5"></label>';
              f = f+'</div>';
              f = f+'<input type="text" name="showName" value="'+data[i]['name']+'" style="margin-left: 5%" readonly>';
              f = f+'<button style = "float:right;margin-right:5%" type="submit">Send</button>';
              f = f+'</form>'
              i = i+1;
              $( "<div/>", {
                  html: f
              }).appendTo( ".insertWithJS" );
         });
      });
</script>
</body>
</html>

"""