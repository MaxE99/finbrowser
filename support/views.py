# Django imports
import re
from django.shortcuts import redirect, render
from django.contrib import messages
# Local imports
from support.forms import SourceSuggestionForm, BugReportForm, FeatureSuggestionForm


def faq(request):
    return render(request, 'support/faq.html')


def report_bug(request):
    if request.method == "POST":
        bug_report_form = BugReportForm(request.POST)
        if bug_report_form.is_valid():
            new_report = bug_report_form.save(commit=False)
            new_report.reporting_user = request.user
            new_report.save()
            messages.success(request,
                             f"Thank you! You're report has been send!")
            return redirect('support:report-bug')
    bug_report_form = BugReportForm()
    context = {'bug_report_form': bug_report_form}
    return render(request, 'support/report_bug.html', context)


def suggestions(request):
    if request.method == "POST":
        feature_suggestion_form = FeatureSuggestionForm(request.POST)
        if feature_suggestion_form.is_valid():
            new_suggestion = feature_suggestion_form.save(commit=False)
            new_suggestion.reporting_user = request.user
            new_suggestion.save()
            messages.success(request,
                             f"Thank you! You're report has been send!")
            return redirect('support:suggestions')
    feature_suggestion_form = FeatureSuggestionForm()
    context = {'feature_suggestion_form': feature_suggestion_form}
    return render(request, 'support/suggestions.html', context)


def privacy_policy(request):
    return render(request, 'support/privacy_policy.html')


def cookie_statement(request):
    return render(request, 'support/cookie_statement.html')


def terms_of_service(request):
    return render(request, 'support/terms_of_service.html')


def suggest_sources(request):
    if request.method == "POST":
        source_suggestion_form = SourceSuggestionForm(request.POST)
        if source_suggestion_form.is_valid():
            new_suggestion = source_suggestion_form.save(commit=False)
            new_suggestion.reporting_user = request.user
            source_suggestion_form.save()
            messages.success(request,
                             f"Thank you! You're report has been send!")
            return redirect('support:suggest-sources')
        else:
            messages.success(request,
                             f"This source has already been suggested!")
            return redirect('support:suggest-sources')
    source_suggestion_form = SourceSuggestionForm()
    context = {'source_suggestion_form': source_suggestion_form}
    return render(request, 'support/suggest_sources.html', context)