from model import entities


def format_to_file_name(a):
    a = a.replace(" ","")
    a = a.replace("_","")
    return a.lower()

def format_to_url(a):
    a = a.replace(" ","_")
    return a.lower()

def rankShows(shows):
    data = []
    for show in shows:
        dic = {}
        dic['name'] = show.name
        dic['rating'] = show.rating
        data.append(dic)
    data = sorted(data, key=lambda k: k['rating'], reverse=True)

    return data