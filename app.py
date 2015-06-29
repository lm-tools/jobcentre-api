from flask import Flask, request, flash, redirect, render_template, json, Response, session, url_for
import jinja2
import os
import mechanize
import re
import urllib2
from ukpostcodeutils import validation

# settings
app = Flask(__name__)
app.secret_key = 'mdkslabnucnchdfbsj'

app.config.update(
    DEBUG = True,
    DIRECT_GOV_URL = 'http://los.direct.gov.uk'
)

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/api")
def api():

	postcode = request.args.get('postcode', '')
	postcode = postcode.replace(' ', '').upper()

	if postcode == '' or not validation.is_valid_postcode(postcode):
			return Response(response="{'message': 'Invalid data'}", status=400, mimetype='application/json')

	data = {}
	br = mechanize.Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

	try:
			br.open(app.config['DIRECT_GOV_URL'])
			br.form = list(br.forms())[0]
			br.form["ctl00$ContentPlaceHolder1$Postcode"] = postcode
			response = br.submit()
			html = response.read()
	except urllib2.URLError:
			return Response(response="{'message': 'Bad gateway - direct.gov.uk not available'}", status=502, mimetype='application/json')

	try:
			#get name
			matches = re.findall('<h3>([^<]*)</h3>', html)
			name = matches[1].strip()

			#get address
			matches = re.search('(.*)<br \/>Telephone', html)
			print  matches
			parts = matches.group(1).strip().split('<br />')
			postcode = parts[len(parts) - 1]
			address = ', '.join(parts)
	except IndexError:
			return Response(response="{'message': 'Bad gateway - error passing data'}", status=502, mimetype='application/json')

	data = {'name': name, 'address':address, 'postcode':postcode, 'opening-times': []}
	return Response(response=json.dumps(data), status=200, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port)
