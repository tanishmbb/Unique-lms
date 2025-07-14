from django.urls import reverse
from django.shortcuts import redirect

def redirect_with_tab(viewname, tab):
    url = f"{reverse(viewname)}?tab={tab}"
    return redirect(url)
