from django.http import HttpResponse

def wsgi(request):
    return HttpResponse("We're optimizing wsgi!")