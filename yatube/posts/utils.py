from django.core.paginator import Paginator

PAGES_FOR_PAGINATOR: int = 7


def page_get(request, post_list):
    paginator = Paginator(post_list, PAGES_FOR_PAGINATOR)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
