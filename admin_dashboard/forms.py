from django import forms
from .models import Pelanggan, Transaksi
from django.contrib.auth.hashers import make_password, check_password

from .models import Karyawan

class PelangganRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label='Konfirmasi Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Pelanggan
        fields = ['username', 'nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp', 'email']
        labels = {
            'username': 'Username',
            'nama_pelanggan': 'Nama Lengkap',
            'alamat': 'Alamat',
            'tanggal_lahir': 'Tanggal Lahir',
            'no_hp': 'Nomor HP',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contoh@email.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        email = cleaned_data.get('email')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Password dan konfirmasi password tidak cocok.")
        
        # Email validation
        if email:
            # Basic email format validation
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError("Format email tidak valid.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class PelangganLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                pelanggan = Pelanggan.objects.get(username=username)
                if not check_password(password, pelanggan.password):
                    raise forms.ValidationError("Username atau password salah.")
                self.pelanggan = pelanggan
            except Pelanggan.DoesNotExist:
                raise forms.ValidationError("Username atau password salah.")
        return cleaned_data

class PelangganEditForm(forms.ModelForm):
    class Meta:
        model = Pelanggan
        fields = ['nama_pelanggan', 'alamat', 'tanggal_lahir', 'no_hp', 'email']
        labels = {
            'nama_pelanggan': 'Nama Lengkap',
            'alamat': 'Alamat',
            'tanggal_lahir': 'Tanggal Lahir',
            'no_hp': 'Nomor HP',
            'email': 'Email',
        }
        widgets = {
            'nama_pelanggan': forms.TextInput(attrs={'class': 'form-control'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_lahir': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'no_hp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contoh@email.com'}),
        }

class PembayaranForm(forms.Form):
    bukti_bayar = forms.FileField(
        label='Bukti Pembayaran',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=True
    )
    catatan = forms.CharField(
        label='Catatan (Opsional)',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )


class TransaksiVerificationForm(forms.ModelForm):
    class Meta:
        from .models import Transaksi
        model = Transaksi
        fields = ['foto_pengiriman', 'status_transaksi']
        widgets = {
            'foto_pengiriman': forms.FileInput(attrs={'class': 'form-control'}),
            'status_transaksi': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned = super().clean()
        # Ensure a photo is provided when marking as SELESAI
        status = cleaned.get('status_transaksi')
        foto = cleaned.get('foto_pengiriman')
        if status == 'SELESAI' and not foto:
            raise forms.ValidationError('Foto verifikasi pengiriman diperlukan saat menandai SELESAI.')
        return cleaned


class KaryawanLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@contoh.com'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            try:
                k = Karyawan.objects.get(email=email)
                if not k.check_password(password):
                    raise forms.ValidationError('Email atau password salah.')
                if not k.is_active:
                    raise forms.ValidationError('Akun tidak aktif.')
                self.karyawan = k
            except Karyawan.DoesNotExist:
                raise forms.ValidationError('Email atau password salah.')
        return cleaned


class KaryawanCreateForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Karyawan
        fields = ['nama', 'email', 'password', 'is_active']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput()
        }

    def save(self, commit=True):
        k = super().save(commit=False)
        raw = self.cleaned_data.get('password')
        if raw:
            k.set_password(raw)
        if commit:
            k.save()
        return k