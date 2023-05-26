from flask import Flask, render_template, request, abort, redirect, url_for
import os
import re
import requests
import logging
import sys
import threading

app = Flask(__name__)

logging.basicConfig(filename='setu.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def download(url):
    pic_res = requests.get(url)
    if pic_res.status_code == 200:
        file_name = url.split('/')[-1]
        with open(f'static/{file_name}', "wb") as f:
            f.write(pic_res.content)
        logging.info(f"{file_name} downloaded successfully.")
        return True  # Return True if download is successful
    else:
        logging.error(f"Download failed for {url}")
        return False  # Return False if download fails


def download_setu(num):
    while num > 0:
        if num > 20:
            count = 20
        else:
            count = num
        num -= count
        url = f'https://api.lolicon.app/setu/v2?r18=1&num={count}&excludeAI=true'
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'}
        res = requests.get(url, headers=headers).text
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = re.findall(pattern, res)
        threads = []
        for i in range(len(urls)):
            t = threading.Thread(target=download, args=(urls[i],))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num = int(request.form['num'])
        download_setu(num)
        return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/files')
def files():
    file_list = os.listdir('static')
    return render_template('files.html', files=file_list)


@app.route('/logs')
def logs():
    with open('setu.log', 'r') as f:
        log_content = f.read()
    return render_template('logs.html', logs=log_content)


@app.route('/downloads')
def downloads():
    file_list = os.listdir('static')
    return render_template('downloads.html', files=file_list)


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('static', filename)
    if os.path.isfile(file_path):
        return redirect(url_for('static', filename=filename, _external=True))
    else:
        abort(404)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message='404 - Not Found'), 404


if __name__ == '__main__':
    app.run()
