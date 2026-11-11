"""Build static learning data and standalone synthetic-data practice notebooks."""
import json, ast
from pathlib import Path
root=Path(__file__).resolve().parents[1]; dist=root/'dist'
guides=json.loads((root/'content/guides.json').read_text()); slides=json.loads((dist/'data/slides.json').read_text())
student='''import numpy as np
import pandas as pd
rng = np.random.default_rng(42)
n = 120
df = pd.DataFrame({
    'student_id': np.arange(1, n+1),
    'name': [f'Student {i}' for i in range(1, n+1)],
    'faculty': rng.choice(['Engineering', 'Science', 'Arts'], n),
    'age': rng.integers(18, 25, n),
    'study_hours': rng.uniform(1, 10, n).round(1),
    'gpa': np.clip(rng.normal(3.0, 0.5, n), 0, 4).round(2),
    'passed_exam': rng.random(n) > 0.2,
})
'''
retail='''import numpy as np
import pandas as pd
rng = np.random.default_rng(42)
n = 600
df = pd.DataFrame({
    'order_id': np.arange(1, n+1),
    'customer_id': rng.integers(1, 81, n),
    'date': pd.Timestamp('2025-01-01') + pd.to_timedelta(rng.integers(0, 730, n), unit='D'),
    'product': rng.choice(['Notebook', 'Pen', 'Bag'], n),
    'region': rng.choice(['North', 'South'], n),
    'price': rng.uniform(50, 500, n).round(2),
    'quantity': rng.integers(1, 6, n),
})
df['category'] = df['product'].map({'Notebook': 'Stationery', 'Pen': 'Stationery', 'Bag': 'Accessories'})
df['revenue'] = df['price'] * df['quantity']
df['cost'] = df['revenue'] * rng.uniform(0.45, 0.85, n)
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.to_period('M').astype(str)
'''
rfm=retail+'''snapshot = df['date'].max() + pd.Timedelta(days=1)
rfm = df.groupby('customer_id').agg(
    recency=('date', lambda s: (snapshot - s.max()).days),
    frequency=('order_id', 'nunique'),
    monetary=('revenue', 'sum'))
# Fixed business thresholds avoid arbitrary tie-breaking; these are illustrative.
rfm['segment'] = np.select(
    [(rfm.recency <= 60) & (rfm.frequency >= 8), rfm.recency > 180],
    ['Champions', 'At risk'], default='Developing')
'''
reg='''import numpy as np
import pandas as pd
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
X, y = make_regression(n_samples=240, n_features=5, noise=25, random_state=42)
X = pd.DataFrame(X, columns=['size', 'marketing', 'footfall', 'staff', 'competitors'])
X.iloc[::17, 0] = np.nan
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
def pipeline(model):
    return Pipeline([('impute', SimpleImputer(strategy='median')),
                     ('scale', StandardScaler()), ('model', model)])
'''
code={
1:retail+'''print('Rows:', df.shape[0])
print('Columns:', df.shape[1])
print('Date range:', df.date.min(), 'to', df.date.max())
print('Unique products:', df['product'].nunique())
print('Total revenue:', round(df.revenue.sum(), 2))
''',
2:student+'''passed = df.loc[df['passed_exam']]
board = passed.groupby('faculty').agg(
    n=('student_id', 'count'), avg_gpa=('gpa', 'mean'),
    hours=('study_hours', 'sum')).sort_values('avg_gpa', ascending=False)
print(board.round(2))
df['rank_in_faculty'] = df.groupby('faculty')['gpa'].rank(ascending=False, method='dense')
print(df.loc[df['rank_in_faculty'] == 1, ['name', 'faculty', 'gpa']])
''',
3:student+'''raw = pd.concat([df, df.iloc[:3]], ignore_index=True)
raw.loc[::9, 'age'] = np.nan
raw['gpa'] = raw['gpa'].astype(str)
raw['faculty'] = ' ' + raw['faculty'].str.lower() + ' '
def clean(raw):
    result = raw.copy().drop_duplicates('student_id')
    result['gpa'] = pd.to_numeric(result['gpa'], errors='coerce')
    result['age'] = result['age'].fillna(result['age'].median())
    result['faculty'] = result['faculty'].str.strip().str.title()
    return result
clean_df = clean(raw)
print('Rows before / after:', len(raw), len(clean_df))
print(clean_df.isna().sum())
assert clean_df.student_id.is_unique
''',
4:student+'''import matplotlib.pyplot as plt
import seaborn as sns
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sns.histplot(data=df, x='gpa', bins=15, ax=axes[0])
sns.boxplot(data=df, x='faculty', y='gpa', ax=axes[1])
plt.tight_layout()
plt.show()
sns.heatmap(df[['gpa', 'study_hours', 'age']].corr(), annot=True, center=0, cmap='coolwarm')
plt.show()
q1, q3 = df.gpa.quantile([.25, .75]); iqr = q3-q1
print(df.loc[(df.gpa < q1-1.5*iqr) | (df.gpa > q3+1.5*iqr)])
print('Now write three hypotheses. Synthetic associations are not real-world evidence.')
''',
5:retail+'''import matplotlib.pyplot as plt
monthly = df.groupby('month').revenue.sum()
category = df.groupby('category').revenue.sum()
region = df.groupby('region').revenue.sum()
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
monthly.plot(ax=axes[0], title='Situation: monthly revenue')
category.plot.bar(ax=axes[1], title='Investigate: category contribution')
region.plot.bar(ax=axes[2], title='Compare: regional revenue')
for ax in axes:
    ax.set_ylabel('Revenue (THB)')
plt.tight_layout()
plt.show()
# Replace these neutral titles with findings supported by the displayed numbers.
# A resolution needs a justified recommendation, not merely a third chart.
''',
6:retail+'''monthly = df.groupby('month').agg(revenue=('revenue','sum'), cost=('cost','sum'))
monthly['growth_pct'] = monthly.revenue.pct_change() * 100
monthly['margin_pct'] = (monthly.revenue-monthly.cost) / monthly.revenue * 100
monthly['rolling_3'] = monthly.revenue.rolling(3).mean()
print(monthly.round(2))
print('Average order value:', df.revenue.sum() / df.order_id.nunique())
print(df.groupby(['region','category']).revenue.sum())
''',
7:retail+'''import plotly.express as px
from pathlib import Path
summary = df.groupby(['category', 'year'], as_index=False).revenue.sum()
monthly = df.groupby(['month','category'], as_index=False).revenue.sum()
figures = [px.bar(summary, x='category', y='revenue', color='year', barmode='group'),
           px.line(monthly, x='month', y='revenue', color='category')]
for fig in figures: fig.show()
html = '<!doctype html><html><head><meta charset="utf-8"><title>Retail report</title></head><body><h1>Synthetic retail report</h1>'
for i, fig in enumerate(figures):
    html += fig.to_html(full_html=False, include_plotlyjs=True if i == 0 else False)
Path('retail-dashboard.html').write_text(html + '</body></html>')
print('Saved a self-contained dashboard. Add three findings and one recommendation.')
''',
8:rfm+'''# Slide-style quantile scores. Small or tied datasets need an explicit policy.
for field, label, labels in [('recency','R',[4,3,2,1]), ('frequency','F',[1,2,3,4]), ('monetary','M',[1,2,3,4])]:
    values = rfm[field]
    try:
        rfm[label] = pd.qcut(values, 4, labels=labels)
    except ValueError:
        # Demonstration fallback only: first-rank splits ties by row order.
        print(f'{field}: tied boundaries; applying documented rank-first fallback')
        rfm[label] = pd.qcut(values.rank(method='first'), 4, labels=labels)
print(rfm.head())
print(rfm.groupby('segment').agg(customers=('recency','size'),
      recency=('recency','mean'), frequency=('frequency','mean'), monetary=('monetary','mean')))
''',
9:rfm+'''from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
features = rfm[['recency','frequency','monetary']]
X = StandardScaler().fit_transform(features)
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    print(k, round(km.inertia_), round(silhouette_score(X, km.labels_), 3))
# Four is illustrative; choose using diagnostics and business usefulness.
rfm['cluster'] = KMeans(n_clusters=4, n_init=10, random_state=42).fit_predict(X)
print(rfm.groupby('cluster')[features.columns].mean().round(1))
print(pd.crosstab(rfm.segment, rfm.cluster))
gmm = GaussianMixture(n_components=4, random_state=42).fit(X)
print('Soft memberships:', gmm.predict_proba(X)[:3].round(2))
''',
10:reg+'''pipe = pipeline(LinearRegression())
cv_rmse = -cross_val_score(pipe, X_train, y_train, cv=5, scoring='neg_root_mean_squared_error')
print('CV RMSE:', cv_rmse.mean())
pipe.fit(X_train, y_train)
preds = pipe.predict(X_test)
print('Held-out RMSE:', np.sqrt(mean_squared_error(y_test, preds)))
print('Held-out R2:', r2_score(y_test, preds))
''',
11:reg+'''# Search the WHOLE pipeline so preprocessing is learned separately within each fold.
search = GridSearchCV(pipeline(LinearRegression()), [
    {'model': [LinearRegression()]},
    {'model': [Ridge()], 'model__alpha': [0.1, 1, 10, 100]},
    {'model': [Lasso(max_iter=10000)], 'model__alpha': [0.01, 0.1, 1, 10]},
], cv=5, scoring='neg_root_mean_squared_error')
search.fit(X_train, y_train)
for params, score in zip(search.cv_results_['params'], search.cv_results_['mean_test_score']):
    print(params, 'CV RMSE:', round(-score, 3))
print('Chosen on training CV:', search.best_params_)
preds = search.predict(X_test)
print('Final held-out RMSE:', np.sqrt(mean_squared_error(y_test, preds)))
print('Final held-out R2:', r2_score(y_test, preds))
''',
12:'''import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, average_precision_score
X, y = make_classification(n_samples=500, n_features=6, n_informative=4,
                           weights=[0.8, 0.2], random_state=42)
X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(6)])
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=.2, random_state=42)
models = {
    'Logistic': make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced', max_iter=1000)),
    'Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
}
for name, model in models.items():
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)
    print(name, 'ROC AUC:', roc_auc_score(y_test, proba), 'Average precision:', average_precision_score(y_test, proba))
    print(confusion_matrix(y_test, preds))
    print(classification_report(y_test, preds, zero_division=0))
# Comparison is educational. Use CV for model selection, then a final untouched test.
'''
}
optional='''# Optional extensions: install shap and xgboost in your notebook environment first.
# %pip install shap xgboost
import shap
from xgboost import XGBClassifier
xgb = XGBClassifier(n_estimators=100, random_state=42)
xgb.fit(X_train, y_train)
print('XGBoost ROC AUC:', roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1]))
rf = models['Forest']
explanation = shap.TreeExplainer(rf)(X_test)
# For binary sklearn forests, SHAP may return (samples, features, outputs).
positive = explanation[:, :, 1] if explanation.values.ndim == 3 else explanation
shap.plots.beeswarm(positive)
shap.plots.waterfall(positive[0])
'''
for g,s in zip(guides,slides):
 g.update(s);g['practice']=code[g['id']];g['optional']=optional if g['id']==12 else ''
 ast.parse(g['practice'])
 cells=[{'cell_type':'markdown','metadata':{},'source':f"# Session {g['id']:02}: {g['title']}\n\nPractice companion for New. **Synthetic demonstration data**, not the lecturer's original dataset. Run the code cells top to bottom. The original slide snippets remain available separately in the website.\n\nRequires numpy, pandas, matplotlib, seaborn, scikit-learn, and plotly. Install missing packages with `%pip install numpy pandas matplotlib seaborn scikit-learn plotly`."},
 {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':g['practice']},
 {'cell_type':'markdown','metadata':{},'source':'## Your turn\n'+g['task']+'\n\n## Watch out\n'+g['pitfall']}]
 if g['optional']:cells += [{'cell_type':'markdown','metadata':{},'source':'## Optional: XGBoost and SHAP\nInstall the optional packages before running this extension.'},{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':optional}]
 (dist/'notebooks'/f'session-{g["id"]:02}.ipynb').write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'cells':[dict(c,id=f's{i}') for i,c in enumerate(cells)]},indent=2))
(dist/'data'/'course.json').write_text(json.dumps(guides,ensure_ascii=False))
print('Built 12 guides and 12 notebooks')
