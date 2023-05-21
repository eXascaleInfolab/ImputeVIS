import datetime
from django.db import models
from django.utils import timezone


# A model is the single, definitive source of information about your data.
# It contains the essential fields and behaviors of the data you’re storing.
# Django follows the DRY Principle.
# The goal is to define your data model in one place and automatically derive things from it.

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
