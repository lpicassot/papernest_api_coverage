from django.urls import path

from .views.coverage import CoverageView

urlpatterns = [
    path('get_coverage/', CoverageView.as_view(), name='get_coverage'),
]