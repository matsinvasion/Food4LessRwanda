from django.http import HttpResponsePermanentRedirect
from django.conf import settings

#middleware to handle any redirects to the incorrect hostname,requires the full hostname to which the middleware will redirect to be in settings.py as:
#        CANON_URL_HOST = 'www.your-domain.com'
    
#    Optionally, you can provide a list of hostnames which should be redirected to CANON_URL_HOST as:
#        CANON_URLS_TO_REWRITE = ['your-domain.com', 'other-domain.com']
#    If this list is not present, then all requests are redirected to CANON_URL_HOST.
    
 #   One drawback of using this middleware in order to handle canonicalization instead of doing it with the web server
 #   is the issues that arise with SSL Certificates. Imagine that you have a valid cert for 'www.your-domain.com'.
 #   When attempting to access 'your-domain.com', customers may get
 #   a warning message about an invalid SSL Cert, and then they'll be redirected to 'www.your-domain.com'.
    

class URLCanonicalizationMiddleware(object):
	def process_view(self,request,view_func,view_args,vieww_kwargs):
		if not settings.DEBUG:
			"""only perform the redirect if not debug mode"""
			protocol = 'https://' if request.is_secure() else 'http://'
			host = get_host(request)
			new_url = ''
			try:
				if host in settings.CANON_URLS_TO_REWRITE:
					new_url = protocol + settings.CANON_URL_HOST + request.get_full_path()
			except AttributeError:
				if host != settings.CANON_URL_HOST:
					new_url = protocol + settings.CANON_URL_HOST + request.get_full_path()
			
			if new_url:
				return HttpResponsePermanentRedirect(new_url)
					
