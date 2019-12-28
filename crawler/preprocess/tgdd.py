from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer

def TGDDFillNAN():
    fill_price = make_column_transformer(
        (['price'], SimpleImputer(strategy='mean')),
    )
    fill_keyboard_light = make_column_transformer(
        (['keyboard_light'], SimpleImputer(strategy='constant', fill_value=0))
    )
