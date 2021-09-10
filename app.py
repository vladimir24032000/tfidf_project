from flask import Flask
from flask import render_template, request, jsonify
import re, math, os

app = Flask(__name__)

base_path = "./files/"

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/upload/<filename>.txt', methods=['POST'])
def upload(filename):

    if len(request.get_data()) == 0:
        return jsonify({'error': 'bad request', 'message': 'File not loaded'}), 400
    json_table = {'words': [], 'df': [], 'tfidf': []}

    #проверка и сохранение иконки
    byteData = request.get_data()

    content = byteData.decode('UTF-8')
    save_file(content, filename)
    tfidf_table = create_tfidf_table(content)
    for item in tfidf_table:
        json_table['words'].append(item[0][0])
        json_table['df'].append(item[0][1])
        json_table['tfidf'].append(item[1])
    return jsonify(json_table)

@app.route('/index')
def index():
    return render_template('index.html', title='Upload file')

def create_tfidf_table(content):
    tf = {}

    max_words_count = 50
    content = content.lower()
    words = re.sub('\W', ' ', content).split()
    words_count = len(words)
    for word in words:
        tf[word] = round(words.count(word)/words_count, 5)
    tf = list(tf.items())
    tf_idf = {}
    i = 0
    for item in tf:
        if i == max_words_count:
            break
        tf = item[1]
        idf = count_idf(item[0])
        tf_idf[item[0], item[1]] = round(idf, 5)
        i = i + 1
    tf_idf = list(tf_idf.items())
    tf_idf.sort(key=lambda x: x[1], reverse=True)
    return tf_idf

def count_idf(word):
    idf = 0
    documents_count = 0
    documents_with_word_count = 0
    print(word)
    for root, dirs, files in os.walk(base_path, topdown=False):
        for name in files:
            newfile = os.path.join(root, name)
            str = open(newfile, 'r').read()
            str = str.lower()
            words = re.sub('\W', ' ', str).split()
            if words.count(word) > 0:
                documents_with_word_count = documents_with_word_count + 1
            documents_count = documents_count + 1

    print(documents_count, documents_with_word_count)
    if documents_with_word_count != 0:
        idf = math.log(documents_count / documents_with_word_count)
    return idf

def save_file(file_content, filename):

    try:

        file_path = os.path.join(base_path, filename + ".txt")
        text_file = open(file_path, "w")

        text_file.write(file_content)
        text_file.close()

    except:
       return jsonify({'error': 'bad request', 'message': 'File not saved'}), 501


if __name__ == '__main__':
    app.run()
