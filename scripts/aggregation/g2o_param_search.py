import time
import numpy as np
from collections import defaultdict
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer

from .g2o_estimator import G2OEstimator
from slam.evaluation import calculate_metrics, normalize_metrics



class DisabledCV:
    def __init__(self):
        self.n_splits = 1

    def split(self, X, y, groups):
        yield (np.where(groups == 0)[0], np.where(groups == 1)[0])

    def get_n_splits(self, X, y, groups=None):
        return self.n_splits

def score(y, preds, metric):
    print(f'Scoring {len(y)} trajectories. Metric: {metric}')
    start_time = time.time()
    scores = []
    for i, (gt_trajectory, predicted_trajectory) in enumerate(zip(y, preds)):
        metrics_dict = calculate_metrics(gt_trajectory, predicted_trajectory)
        metrics_dict = normalize_metrics(metrics_dict)
        score = metrics_dict[metric]
        scores.append(score)
    
    average_score = np.mean(scores)
    print(f'Scoring completed in {time.time() - start_time:.3f} s\n') 
    return average_score    
       
    
def ate(X, y):
    return score(X, y, 'ATE')


def rmse_t(X, y):
    return score(X, y, 'RMSE_t')


def rmse_r(X, y):
    return score(X, y, 'RMSE_r')


def rpe_t(X, y):
    return score(X, y, 'RPE_t')


def rpe_r(X, y):
    return score(X, y, 'RPE_r')


def random_search(X, y, groups, param_distributions, **kwargs):
    
    score = {'ATE': make_scorer(ate, greater_is_better=False),
               'RMSE_t': make_scorer(rmse_t, greater_is_better=False),
               'RMSE_r': make_scorer(rmse_r, greater_is_better=False),
               'RPE_t': make_scorer(rpe_t, greater_is_better=False),
               'RPE_r': make_scorer(rpe_r, greater_is_better=False)}
    
    print(f'Number of predicted trajectories {len(X)}')
    print(f'Number of gt trajectories {len(y)}')
    print(f'Number of train trajectories {len(groups) - sum(groups)}')
    print(f'Number of test trajectories {sum(groups)}')
    print(groups)
    rs = RandomizedSearchCV(G2OEstimator(verbose=True), 
                            param_distributions,
                            cv=DisabledCV(),
                            refit=False,
                            **kwargs)
    rs.fit(X, y, groups)

    return pd.DataFrame(rs.cv_results_)
