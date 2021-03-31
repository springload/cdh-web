from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


class DateRange(models.Model):
    '''Abstract model with start and end dates. Includes
    validation that requires end date falls after start date (if set),
    and custom properties to check if dates are current/active and to
    display years.'''

    #: start date
    start_date = models.DateField()
    #: end date (optional)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_current(self):
        '''is current: start date before today and end date
        in the future or not set'''
        today = date.today()
        return self.start_date <= today and \
            (not self.end_date or self.end_date >= today)

    @property
    def years(self):
        '''year or year range for display'''
        val = str(self.start_date.year)

        if self.end_date:
            # start and end the same year - return single year only
            if self.start_date.year == self.end_date.year:
                return val

            return '%s–%s' % (val, self.end_date.year)

        return '%s–' % val

    def clean_fields(self, exclude=None):
        if exclude is None:
            exclude = []
        if 'start_date' in exclude or 'end_date' in exclude:
            return
        # require end date to be greater than start date
        if self.start_date and self.end_date and \
                not self.end_date >= self.start_date:
            raise ValidationError('End date must be after start date')
