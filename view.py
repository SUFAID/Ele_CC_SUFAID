from flask import Flask, render_template, request
import re,json
from dateutil.parser import parse
from datetime import datetime
app = Flask(__name__)

@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_files():
   if request.method == 'POST':
	  	try:
			str_data = request.files['file'].read()
	  		json_data= str_data[str_data.find('{'):str_data.rfind('}')+1]
			dct_data=json.loads(json_data)
		except:
			return "In valid json formate."
		
		if not dct_data.has_key("messages"):
			return "Json key should be messeges."
		lst_data = dct_data["messages"]
		try:
			lst_response = main(lst_data)
		except Exception as E:
			return "Somthing went wrong."
		return render_template('listing.html', data=lst_response)
def main(lst_sms):
	lst_data = []
	for sms in lst_sms:
		if re.search('credit\s*card|debi\s*card', sms["text"], re.IGNORECASE):
			sms["text"] = sms["text"].replace("\\","")
			amount = re.search('rs\.?\s*[,\d]+\.?\d{0,2}|inr\.?\s*[,\d]+\.?\d{0,2}', sms["text"],re.IGNORECASE)
			account_no = re.search('[Xx\*]+\s*[\-0-9]{3,}|ending\s*\d{,4}',sms["text"],re.IGNORECASE )
			str_date = re.search('\d{0,4}[\:\-\/]\w*[\:\-\/]\d{0,4}',sms["text"])
			str_time = re.search('\d{0,2}:\d{0,2}:\d{0,2}\s',sms["text"])
			
			# skip if any of the amount,str_date,account_no is empty 
			if not (amount and str_date and account_no):
				continue
			amount = amount.group()
			account_no = account_no.group()
			str_date = str_date.group()
			
			if str_time :
				str_time = str_time.group()
				str_date += " "+str_time
			
			dct_data = {}
			dct_data["amount"] = re.sub('^[^0-9]+','',amount)
			dct_data["account_no"] = re.sub('[^0-9]+','xxxx',account_no)
			
			try:
				#date format conversion 
				dct_data["trn_date"] = date_time_conversion(str_date)
			except:
				dct_data["trn_date"] = ""
			dct_data["sms_date"] = date_time_conversion(sms["datetime"])
			dct_data["sender_id"] = sms["number"].split("-",1)[-1]
			dct_data["time_stamp"] = sms["timestamp"]
			lst_data.append(dct_data)
			
			#sorting based on sms date
			lst_data = sorted(lst_data,key=lambda x:x["time_stamp"],reverse=1)
	return lst_data	

def date_time_conversion(date_time):
	date_time = parse(date_time)
	str_date = datetime.strftime(date_time, '%d-%b-%Y %I:%M%p')
	return str_date

if __name__ == '__main__':
   app.run(debug = True)

