from django.db import models
from django.contrib.auth.models import User


class JournalEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_text = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entry by {self.user.username} at {self.datetime}"
    

class Results(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    positive_percentage = models.FloatField()
    negative_percentage = models.FloatField()
    neutral_percentage = models.FloatField()

    def __str__(self):
        return f"Results for Entry ID {self.entry_id}"