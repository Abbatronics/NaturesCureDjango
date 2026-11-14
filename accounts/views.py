from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import EmailOTP
import random













def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')




User = get_user_model()

def send_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')

        # Save name/password for after verification
        request.session['otp_name'] = name
        request.session['otp_email'] = email
        request.session['otp_password'] = password

        # Delete old OTPs for this email
        EmailOTP.objects.filter(email=email).delete()

        code = str(random.randint(100000, 999999))
        EmailOTP.objects.create(email=email, code=code)

        send_mail(
            'Your NaturesCure OTP Code',
            f'Hello {name},\n\nYour verification code is: {code}\n\nE go expire in 5 minutes. No share am with anybody.\n\n- NaturesCure Team',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return redirect('verify_otp')
    return render(request, 'account/send_otp.html')

def verify_otp_view(request):
    email = request.session.get('otp_email')
    if not email:
        return redirect('send_otp')

    if request.method == 'POST':
        entered_code = request.POST.get('code')
        otp = EmailOTP.objects.filter(email=email, code=entered_code, is_used=False).last()

        if otp and not otp.is_expired():
            otp.is_used = True
            otp.save()

            # Create user now - use full_name, NOT first_name/last_name
            name = request.session.get('otp_name', '')
            password = request.session.get('otp_password')

            user, created = User.objects.get_or_create(
                email=email, 
                defaults={'full_name': name}
            )
            if created:
                user.set_password(password)
                user.save()
            else:
                # User don exist before, just login am
                pass

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Clear session
            for k in ['otp_name','otp_email','otp_password']:
                request.session.pop(k, None)
            return redirect('dashboard')
        else:
            return render(request, 'account/verify_otp.html', {'error': 'Code no correct or e don expire. Try again.', 'email': email})

    return render(request, 'account/verify_otp.html', {'email': email})