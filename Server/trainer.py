import numpy as np
import random
from sklearn.cluster import MiniBatchKMeans
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.colors as cl
from matplotlib.figure import Figure
from joblib import dump, load


class MiniBatchKMeansTrainer(object):

    def __init__(self, data, n_clusters=8, resolution = 0.02):
        self.plt = plt
        self.resolution = resolution
        self.data, self.test = self.split(data)
        self.kmeans = self._load_existing_model(data, n_clusters, np.size(self.data, 0))
        self.resolution = resolution



    def split(self, data):
        return data[:int(np.size(data, 0) * 0.9), :], data[int(np.size(data, 0) * 0.9):, :] 

    def _load_existing_model(self, data, n_clusters, batch_size):
        try:
            return load('test.joblib')
        except Exception:
            return MiniBatchKMeans(n_clusters=n_clusters, batch_size=batch_size)

    def partial_fit(self, data = None):
        if type(data) == None:
            self.kmeans.partial_fit(self.data)
        else:
            self.kmeans.partial_fit(data)
            
    def plot_decision_regions(self,b = None,  test_idx=None):
        if type(b) == None:
            X = self.data
        else:
            X = b
        markers = ('s', 'x', 'o', '^', 'v')
        colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan', 'yellow', 'indigo', 'wheat', 'tan', 'darkcyan',
            'royalblue', 'pink', 'powderblue', 'tomato', 'black', 'orange', 'indigo')
        cmap = ListedColormap(colors[:9])
        # plot the decision surface
        x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1

        xx1, xx2= np.meshgrid(np.arange(x1_min, x1_max, self.resolution), np.arange(x2_min, x2_max, self.resolution))
        Z = self.kmeans.predict(np.array([xx1.ravel(), xx2.ravel()]).T)
        Z = Z.reshape(xx1.shape)
        self.plt.contourf(xx1, xx2, Z, alpha=0.4, cmap=cmap)
        self.plt.xlim(xx1.min(), xx1.max())
        self.plt.ylim(xx2.min(), xx2.max())
        result = self.kmeans.predict(self.test)
        for idx, cl in enumerate(np.unique(result)):
            self.plt.scatter(x=self.test[result==cl,0], y=self.test[result==cl,1], alpha=0.8, c=cmap(idx), marker=markers[idx % 5], label=cl)
        plt.show()

    def run_test_cycle(self):
        a = np.zeros((1440, 2))
        b = np.zeros((1440, 2))
        for j in range(2):
            if not j:
                a[:, j] = np.random.normal(900, 1.0, (1440))
            else:
                a[:, j] = np.random.normal(100, 0.5, (1440))

        for j in range(2):
            if not j:
                b[:, j] = np.random.normal(900, 1.0, (1440))
            else:
                b[:, j] = np.random.normal(100, 0.5, (1440))
        
        self.partial_fit(a)

        self.plot_decision_regions(b)
        dump(self.kmeans, 'test.joblib')


def main():
    a = np.zeros((1440, 2))
    b = np.zeros((1440, 2))

    for j in range(2):
        if not j:
            a[:, j] = np.random.normal(900, 1.0, (1440))
        else:
            a[:, j] = np.random.normal(100, 0.5, (1440))

    for j in range(2):
        if not j:
            b[:, j] = np.random.normal(900, 1.0, (1440))
        else:
            b[:, j] = np.random.normal(100, 0.5, (1440))


    kmeans = MiniBatchKMeansTrainer(a, n_clusters=9, resolution=2)
    kmeans.partial_fit(a)

    c = kmeans.kmeans.predict(b)
    kmeans.plot_decision_regions(b)
    dump(kmeans.kmeans, 'test.joblib')
    while True:
        kmeans.run_test_cycle()

if __name__ == "__main__":
    main()