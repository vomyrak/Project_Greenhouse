import numpy as np
import random
from sklearn.cluster import MiniBatchKMeans
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.colors as cl
from matplotlib.figure import Figure
from joblib import dump, load


class MiniBatchKMeansTrainer(object):

    def __init__(self, batch_size = 1440, n_clusters=81, resolution = 0.02, init_info = "k-means++"):
        self.plt = plt
        self.resolution = resolution
        self.batch_size = batch_size
        self.kmeans = self._load_existing_model(n_clusters, batch_size, init_info)
        self.resolution = resolution

    def _load_existing_model(self, n_clusters, batch_size, init_info):
        ''' load existing training model '''
        try:
            return load('test.joblib')
        except Exception:
            return MiniBatchKMeans(n_clusters=n_clusters, batch_size=batch_size, init= init_info)

    def partial_fit(self, data):
        self.kmeans.partial_fit(data)
        dump(self.kmeans, 'test.joblib')
            
    def plot_decision_regions(self, data):
        # plot decision regions
        X = data
        markers = ('s', 'x', 'o', '^', 'v')
        colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan', 'yellow', 'indigo', 'wheat', 'tan', 'darkcyan',
            'royalblue', 'pink', 'powderblue', 'tomato', 'black', 'orange', 'indigo')

        # initialise colour map
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
        result = self.kmeans.predict(X)

        # scatter plot of individual data points
        for idx, cl in enumerate(np.unique(result)):
            self.plt.scatter(x=X[result==cl,0], y=X[result==cl,1], alpha=0.8, c=cmap(idx), marker=markers[idx % 5], label=cl)
        plt.show()  # if showing is required


    def generate_random_data_two_features(self):
        '''Generate Gaussian random data to acceleration training for demonstration'''
        data = np.zeros((1440, 2))
        for j in range(2):
            if not j:
                data[:, j] = np.random.normal(900, 1.0, (1440))
            else:
                data[:, j] = np.random.normal(100, 0.5, (1440))
        return data
        
    def run_test_cycle(self):
        '''Use randomly generated data for testing'''
        a = self.generate_random_data_two_features()
        b = self.generate_random_data_two_features()
        self.partial_fit(a)
        self.plot_decision_regions(b)



def main():
    ''' testing script '''
    kmeans = MiniBatchKMeansTrainer(n_clusters=9, resolution=2)
    a = kmeans.generate_random_data_two_features()
    b = kmeans.generate_random_data_two_features()
    kmeans.partial_fit(a)
    c = kmeans.kmeans.predict(b)
    kmeans.plot_decision_regions(b)
    dump(kmeans.kmeans, 'test.joblib')
    while True:
        kmeans.run_test_cycle()

if __name__ == "__main__":
    main()