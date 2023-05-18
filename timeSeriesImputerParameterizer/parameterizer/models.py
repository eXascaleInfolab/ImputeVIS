from django.db import models


# A model is the single, definitive source of information about your data.
# It contains the essential fields and behaviors of the data you’re storing.
# Django follows the DRY Principle.
# The goal is to define your data model in one place and automatically derive things from it.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)