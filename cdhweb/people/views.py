from django.shortcuts import render


def speakerlist_gone(request):
    # return 410 gone for speakers list view;
    # (removed in 3.0, no longer needed after the Year of Data)
    return render(
        request,
        "404.html",
        context={
            "error_code": 410,
            "message": "That page isn't here anymore.",
            "page_title": "Error — no longer available",
        },
        status=410,
    )
