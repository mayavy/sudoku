from datetime import date, datetime, timezone
from re import A
import uuid
from django.core.validators import MinLengthValidator

from django.db import models

from numpy import size

from users.models import CustomUser

# Create your models here.


def plural(quantity):
    if quantity > 1:
        return 's'
    else:
        return ''


class PostModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    datecreated = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, editable=False)

    class Meta:
        abstract = True

    @property
    def name_short(self):
        return self.author.__str__()[:2]

    @property
    def show_time(self):
        delta = datetime.now(timezone.utc)-self.datecreated
        delta = delta.days*24*60 + delta.seconds//60  # all minutes
        month = delta//(60*24*30)
        if month >= 1:
            pl = plural(month)
            return f'{month}-month{pl} ago'
        else:
            week = delta//(60*24*7)
            pl = plural(week)
            if week >= 1:
                return f'{week}-week{pl} ago'
            else:
                day = delta//(60*24)
                pl = plural(day)
                if day >= 1:
                    return f'{day}-day{pl} ago'
                else:
                    hour = delta//(60)
                    pl = plural(hour)
                    if hour >= 1:
                        return f'{hour}-hour{pl} ago'
                    else:
                        minute = delta
                        pl = plural(minute)
                        return f'{minute}-minute{pl} ago'


class SudokuModel(PostModel):
    sudokustr = models.CharField(max_length=81, validators=[
        MinLengthValidator(81)], null=True)
    story = models.CharField(max_length=1000, null=True)
    solutionstr = models.CharField(max_length=81, validators=[
        MinLengthValidator(81)], null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CommentModel(PostModel):
    comment = models.CharField(max_length=300,  null=True, )
    parentsudoku = models.ForeignKey(
        SudokuModel, on_delete=models.CASCADE,  editable=False)
