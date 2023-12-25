from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import user_registration, sentireader, list_journal_entries, create_journal_entry, retrieve_update_delete_journal_entry, get_results, me

urlpatterns = [
    path('results/', get_results, name='get_results'),
    path('journal-entries/', list_journal_entries, name='journal-entries'),
    path('journal-entries/create/', create_journal_entry, name='create-journal-entry'),
    path('journal-entries/<int:entry_id>/', retrieve_update_delete_journal_entry, name='retrieve_update-delete-journal-entry'),
    path('register/', user_registration, name='user_registration'),
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
    path('me/', me, name='me'),
    path('sentireader/', sentireader, name='sentireader')
]