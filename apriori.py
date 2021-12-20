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
        print (self.frequentItemsets)
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
        return rules

    def difference(self, item, left_subset):
        return tuple(x for x in item if x not in left_subset)
    
    def getConfidence(self, subsetCount, itemsetCount):
        return float(itemsetCount)/subsetCount
        
def main():
    products = defaultdict(list)

    # Get Itemsets From Input Data 

    inputData = pd.read_csv('./inputData/sampleOrderData.csv')

    transactions = inputData.groupby('order_id')['product_id'].apply(list).to_dict()
    reorderedTransactions = inputData.loc[inputData['reordered'] == 1].groupby('order_id')['product_id'].apply(list).to_dict()
    
    itemsets = list(transactions.values())
    reorderedItemset = list(reorderedTransactions.values())

    # Get Unique Itemsets

    # uniqueItemset = []

    # for reorderedItem in reorderedItemset :
    #     if reorderedItem not in itemsets :
    #         itemsets.append(reorderedItem)

    # for itemset in itemsets :
    #     if itemset not in uniqueItemset :
    #         uniqueItemset.append(itemset)
    
    # itemsets = uniqueItemset

    for reorderedItem in reorderedItemset :
            itemsets.append(reorderedItem)
    
    productsData = pd.read_csv('./inputData/sampleProductData.csv')
    products = productsData['product_id'].tolist()

    apriori = Apriori(itemsets, products, 0.2, 0.27)
    frequentItemsets = apriori.getFrequentItemsets()
    a.genRules(frequentItemsets)


if __name__ == '__main__':
    main()