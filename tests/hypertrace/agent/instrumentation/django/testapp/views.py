from django.http import JsonResponse

def path_variable(request, id):
    return JsonResponse({"data": id})