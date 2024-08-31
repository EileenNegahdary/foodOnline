from datetime import date, datetime, time
from django.db import models
from django.utils import timezone
import pytz
from accounts.models import User, UserProfile 
from accounts.utils import send_notification_email

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendors/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    

    def is_open(self):
        # get current day
        today_date = date.today()
        today = today_date.isoweekday()
        
        current_day_hours = AvailableHour.objects.filter(vendor=self, day=today)
        
        # specify the timezone for Iran
        iran_timezone = pytz.timezone('Asia/Tehran')
        # get the current time in Iran timezone and change the format
        current_time = timezone.now().astimezone(iran_timezone).strftime("%H:%M:%S")

        is_open = None
        for hour in current_day_hours:            
            start = str(datetime.strptime(hour.from_hour, "%I:%M %p").time())
            end = str(datetime.strptime(hour.to_hour, "%I:%M %p").time())
            if current_time > start and current_time < end:
                is_open = True
            else:
                is_open = False
        
        return is_open

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    email_subject ='Congratulations! Your account has been approved.'
                else:
                    email_subject = "We're sorry. You're not eligible for publishing your food menu on our website."

                send_notification_email(email_subject, template, context)
            
                
        return super(Vendor, self).save(*args, **kwargs)
    

DAYS =  [
    (1, ('Monday')),
    (2, ('Tuesday')),
    (3, ('Wednesday')),
    (4, ('Thursday')),
    (5, ('Friday')),
    (6, ('Saturday')),
    (7, ('Sunday')),
]

# generates [('12:00 AM', '12:00 AM'), ('12:30 AM', '12:30 AM'), ('01:00 AM', '01:00 AM'), ..., ('11:00 PM', '11:00 PM'), ('11:30 PM', '11:30 PM')]
HOURS_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]
class AvailableHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)


    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')


    def __str__(self):
        return self.get_day_display()
