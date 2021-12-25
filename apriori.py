## Associate Rule By Apriori
import collections
import csv
import pandas as pd
import numpy as np
import itertools
from collections.abc import Iterable
from itertools import combinations

try:
    defaultdict = collections.defaultdict
except AttributeError:
    defaultdict = collections

class Apriori:
    def __init__(self, itemsets, products, minSupport, minConfidence):
        self.transactions = defaultdict(list)
        self.freqItemset = defaultdict(int)    # danh sách tập phổ biến
        self.itemsets = itemsets                # itemset
        self.totalItemsets = len(itemsets)
        self.frequentItemsets = defaultdict(list)
        self.products = products
        self.minSupport = minSupport
        self.minConfidence = minConfidence

        for i in range(len(itemsets)):
            self.transactions[i] = itemsets[i]

    def getFrequentItemsets(self):
        candidate = {}
        self.get1_freqItemset()
        k = 2
        while len(self.frequentItemsets[k-1]) != 0:
            candidate[k] = self.candidateGen(k)
            for t in self.transactions.items():
                for c in candidate[k]:                    
                    if set(c).issubset(t[1]):
                        self.freqItemset[c] += 1
            self.frequentItemsets[k] = self.prune(candidate[k], k)
            k += 1
        # print (self.frequentItemsets)
        return self.frequentItemsets
    
    def prune(self, items, k):
        f = []
        for item in items:
            count = self.freqItemset[item]
            support = self.getSupport(count)
            if support >= self.minSupport:
                f.append(item)
        return f

    def candidateGen(self, k):
        candidate = []

        if k == 2:
            candidate = [tuple(sorted([x, y])) for x in self.frequentItemsets[k-1] for y in self.frequentItemsets[k-1] if len((x, y)) == k and x != y]
        else:
            candidate = [tuple(set(x).union(y)) for x in self.frequentItemsets[k-1] for y in self.frequentItemsets[k-1] if len(set(x).union(y)) == k and x != y]
        
        # Remove the candidate have subset is not freq
        for c in candidate:
            subsets = self.genSubsets(c)
            for subset in subsets :
                if (subset in candidate) and (subset not in self.frequentItemsets[k-1]):
                    candidate.remove(subset)

        return set(candidate)
    
    def genSubsets(self, item):
        subsets = []
        for i in range(1,len(item)):
            subsets.extend(itertools.combinations(item, i))
        return subsets

    def get1_freqItemset(self):

        for product in self.products:
            for itemset in self.itemsets :
                self.freqItemset[product] += (itemset.count(product))

        for item, count in self.freqItemset.items():
            support = self.getSupport(count)
            if support >= self.minSupport:
                self.frequentItemsets[1].append(item)

    def getSupport(self, supportCount):
        return float(supportCount)/self.totalItemsets

    def genRules(self, frequentItemsets):
        rules = []
        for k, itemset in frequentItemsets.items():
            if k >= 2:
                for item in itemset:
                    subsets = self.genSubsets(item)
                    for left_subset in subsets:
                        if len(left_subset) == 1:
                            subCount = self.freqItemset[left_subset[0]]
                        else:
                            subCount = self.freqItemset[left_subset]
                        itemCount = self.freqItemset[item]
                        if subCount != 0:
                            confidence = self.getConfidence(subCount, itemCount)
                            if confidence >= self.minConfidence:
                                support = self.getSupport(self.freqItemset[item])
                                right_subset = self.difference(item, left_subset)
                                # if len(right_subset) == 1:
                                rules.append((left_subset, right_subset, support, confidence))
                                
        # print(rules)
        # df = pd.DataFrame(rules, columns=['left_subset','right_subset','support','confidence'])
        # df.to_csv('Sample_0.2_0.5.csv', index=False)
        return rules

    def difference(self, item, left_subset):
        return tuple(x for x in item if x not in left_subset)
    
    def getConfidence(self, subsetCount, itemsetCount):
        return float(itemsetCount)/subsetCount

def main():
    products = defaultdict(list)

    # Get Transactions From Input Data 

    inputData = pd.read_csv('./inputData/sampleOrderData.csv')
    # inputData = pd.read_csv('./inputData/order_products__prior.csv')  # 1804 transaction
    # inputData = pd.read_csv('./inputData/order_products__prior2000.csv')
    # inputData = pd.read_csv('./inputData/order_products__prior5000.csv')  # 8860 transaction

    transactions = inputData.groupby('order_id')['product_id'].apply(list).to_dict()
    reorderedTransactions = inputData.loc[inputData['reordered'] == 1].groupby('order_id')['product_id'].apply(list).to_dict()
    
    itemsets = list(transactions.values())
    reorderedItemset = list(reorderedTransactions.values())

    for reorderedItem in reorderedItemset :
            itemsets.append(reorderedItem)
    
    print(itemsets)
    
    productsData = pd.read_csv('./inputData/sampleProductData.csv')
    # productsData = pd.read_csv('./inputData/products.csv')

    products = productsData['product_id'].tolist()

    apriori = Apriori(itemsets, products, 0.2, 0.5)
    frequentItemsets = apriori.getFrequentItemsets()
    apriori.genRules(frequentItemsets)

'''
API getRule return all rules
Read Result CSV File
left_subset, right_subset, support, confidence
Output format:
result
{file: str,
minSup: ,
minconfi 
rules: [
    {
        leftItemset: ['A','B'],
        rightItemset: ['A','B'],
        support: a,
        confidence: b

    },
    {

    }
]}

'''

def getProductName(productIds, products):
    productName = []
    productIds = productIds.strip('(),').split(',') 
    newProductIds = []

    for productId in productIds:
        newProductIds.append(int(productId))

    for newProductId in newProductIds:
        productName.append(products[newProductId])

    return productName

def getRules(outputFile, productFile, minSupp, minConf):
    products = defaultdict(list)
    result = {}
    items = []

    outputData = pd.read_csv(outputFile).apply(list).to_dict('records')
    productsData = pd.read_csv(productFile).apply(list).to_dict('records')

    for item in productsData:
        products[item['product_id']] = item['product_name']

    for item in outputData:
        items.append({
            'left': getProductName(item['left_subset'], products),
            'right': getProductName(item['right_subset'], products),
            'support': item['support'],
            'confidence' : item['confidence']
        })

    result['outputFile'] = outputFile
    result['minSupp'] = minSupp
    result['minConf'] = minConf
    result['items'] = items

    print(result)
    return result

def getDemoProducts():
    transactions = []
    products = []
    inputData = pd.read_csv('./inputData/demoDataSet.csv',names=['transactions'],header=None)
    transactions = list(inputData["transactions"].apply(lambda x:x.split(',')))
    for item in transactions:
        products += item
    products = list(set(products))
    return products

def processDemoData(minSupp, minConf):
    #PreProcess

    transactions = []
    products = []
    inputData = pd.read_csv('./inputData/demoDataSet.csv',names=['transactions'],header=None)
    transactions = list(inputData["transactions"].apply(lambda x:x.split(',')))
    for item in transactions:
        products += item
    products = set(products)

    # Gen Rule Use Apriori Algorithm
    result = {}
    items = []
    apriori = Apriori(transactions, products, minSupp, minConf)
    frequentItemsets = apriori.getFrequentItemsets()
    rules = apriori.genRules(frequentItemsets)
    for item in rules:
        items.append({
            'left': list(item[0]),
            'right': list(item[1]),
            'support': item[2],
            'confidence' : item[3]
        })
    result['minSupp'] = minSupp
    result['minConf'] = minConf
    result['items'] = items
    print(result)
    return result

if __name__ == '__main__':
    processDemoData(0.2, 0.5)

    # main()
    # getRules('outputData/1000Tran_0.01_0.3.csv','inputData/products.csv')
    # getRules('outputData/2000Tran_0.01_0.3.csv','inputData/products.csv')
    # getRules('outputData/5000Tran_0.01_0.3.csv','inputData/products.csv')