from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(queryset, current_page, per_page=6):
    # Paginate all items by per_page
    paginator = Paginator(queryset, per_page)
    # Try to get the ?page=x value
    try:
        # If the page exists and the ?page=x is an int
        items = paginator.page(current_page)
    except PageNotAnInteger:
        # If the ?page=x is not an int; show the first page
        items = paginator.page(1)
    except EmptyPage:
        # If the ?page=x is out of range (too high most likely)
        # Then return the last page
        items = paginator.page(paginator.num_pages)
    return items


def query_param_to_list(query_param, as_int=False):
    if query_param:
        # convert to list and remove empty items
        query_param_list = filter(None, query_param.split(','))

        if as_int:
            # convert to int
            query_param_list = map(int, query_param_list)

        try:
            return list(query_param_list)
        except ValueError:
            # TODO: Return error message
            pass

    return None