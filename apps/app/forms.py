from django import forms


class SearchForm(forms.Form):
	city = forms.CharField(max_length=255)
	query = forms.CharField(max_length=255)
	grid_size = forms.IntegerField(min_value=1, max_value=50, initial=10)


class SendEmailForm(forms.Form):
	location = forms.CharField(max_length=255)
	subject = forms.CharField(max_length=255)
	text = forms.CharField(widget=forms.Textarea)
	delay_min = forms.IntegerField(min_value=0, required=False)

	def clean_delay_min(self):
		val = self.cleaned_data.get('delay_min')
		if val is None:
			return 1
		return val


class LoginForm(forms.Form):
	username = forms.CharField(max_length=150)
	password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
	username = forms.CharField(max_length=150)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput, min_length=6)
	language = forms.CharField(max_length=8, initial='pl')
	country = forms.CharField(max_length=8, initial='PL')
	credentials = forms.FileField()

