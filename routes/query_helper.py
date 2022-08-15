def get_query_by_page(filter_by, int_page):
    try:
        clips_response = filter_by.paginate(page=int_page, per_page=100).items
    except:
        clips_response = []
    return clips_response
