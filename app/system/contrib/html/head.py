""" Head helpers for generating html data """

def add_metadata(keywords, description):
    data = list()
    data.append("<meta name=\"description\" content=\"%s\" />" % (description,))
    data.append("<meta name=\"keywords\" content=\"%s\" />" % (keywords,))
    return "\n".join(data)
