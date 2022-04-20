from django.shortcuts import render


def faq(request):
    return render(request, 'support/faq.html')


def report_bug(request):
    if request.method == "POST":
        reportArea = request.POST['reportArea'],
        reportTopic = request.POST['reportTopic'],
        reportExplanation = request.POST['reportExplanation'],
        return render(request, 'support/report_bug.html',
                      {'reportTopic': reportTopic})
    else:
        return render(request, 'support/report_bug.html')


def suggestions(request):
    if request.method == "POST":
        suggestionArea = request.POST['suggestionArea'],
        suggestionType = request.POST['suggestionType'],
        suggestionExplanation = request.POST['suggestionExplanation'],
        return render(request, 'support/suggestions.html',
                      {'suggestionType': suggestionType})
    else:
        return render(request, 'support/suggestions.html')


def privacy_policy(request):
    return render(request, 'support/privacy_policy.html')


def cookie_statement(request):
    return render(request, 'support/cookie_statement.html')


def terms_of_service(request):
    return render(request, 'support/terms_of_service.html')