from flask import Flask, request, jsonify
from flask_cors import CORS
from apriori import getRules, processDemoData, getDemoProducts

app = Flask(__name__)
CORS(app)

@app.route('/get-rules-sample', methods=['GET'])
def getRuleSample():
    return getRules('outputData/Sample_0.2_0.5.csv','inputData/sampleProductData.csv', 0.2, 0.5)

@app.route('/get-rules-1000', methods=['GET'])
def getRule1000():
    return getRules('outputData/1000Tran_0.01_0.3.csv','inputData/products.csv', 0.01, 0.3)

@app.route('/get-rules-2000', methods=['GET'])
def getRule2000():
    return getRules('outputData/2000Tran_0.01_0.3.csv','inputData/products.csv', 0.01, 0.3)

@app.route('/get-rules-5000', methods=['GET'])
def getRule5000():
    return getRules('outputData/5000Tran_0.01_0.3.csv','inputData/products.csv', 0.01, 0.3)

@app.route('/get-demo-products', methods=['GET'])
def getProducts():
    return jsonify( products = getDemoProducts())

@app.route('/get-rules-demo', methods=['POST'])
def getRuleDemo():
    data = request.get_json()
    return processDemoData(float(data.get("minSupp")),float(data.get("minConf")))

if __name__ == '__main__':
    app.run(debug = True)