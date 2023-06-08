import pandas as pd
import sys,os
from dataclasses import dataclass
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor
)
from sklearn.metrics import r2_score

from src.exception import CustomException
from src.logger import logging
from src.utils import save_obj,evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path=os.path.join("artifact","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config=ModelTrainerConfig()

    def initiate_model_trainer(self,train_array,test_array):
        try:
            logging.info("Splitting training and test Data ")
            x_train,y_train,x_test,y_test=[
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1]
            ]
            models= {
                'Linear Regression':LinearRegression(),
                'Decision Tree':DecisionTreeRegressor(),
                'Random Forest':RandomForestRegressor(),
                'Gradient Boosting':GradientBoostingRegressor(),
                'catboost':CatBoostRegressor(),
                'xgboost':XGBRegressor(),
                'AdaBoost':AdaBoostRegressor()             
                }
            params={
                "Decision Tree":{'criterion':['squared_error','friedman_mse','absolute_error','poisson']},
                                 #'splitter':['best','random'],
                                 #'max_features':['auto','sqrt','log2']},
                "Random Forest":{'n_estimators':[10,30,90,240]},
                    #'criterion':['squared_error','friedman_mse','absolute_error','poisson']},
                "AdaBoost":{'learning_rate':[0.1,0.5,0.01,0.05]
                            #,'n_estimators':[10,30,90,240],
                            # #'loss':['linear','square','exponential']
                            },
                "Linear Regression":{},
                "Gradient Boosting":{#'loss':['squared_error','absolute_error','huber','quantile'],
                                     'learning_rate':[0.1,0.2,0.01,0.05],
                                     #'n_estimators':[10,30,90,240],
                                     'subsample':[0.6,0.7,0.8,0.9],
                                     },
                "xgboost":{'learning_rate':[0.1,0.5,0.01,0.05],
                                     'n_estimators':[100,150,200,250]},
                "catboost":{'learning_rate':[0.2,0.01,0.03,0.05],
                            'iterations':[10,40,80,100]}
            }
            model_report:dict=evaluate_models(x_train=x_train,y_train=y_train,x_test=x_test,y_test=y_test,models=models,params=params)
            best_model_score=max(sorted(model_report.values()))
            best_model_name=list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model=models[best_model_name]

            if best_model_score<0.6 :
                raise CustomException("No best model found")
            

            save_obj(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predictions=best_model.predict(x_test)
            r2_scores=r2_score(y_test,predictions)
            logging.info(f"Best model found with r2 scores:{r2_scores*100}")

            return r2_scores*100,best_model

        except Exception as e:
            raise CustomException(e,sys)
