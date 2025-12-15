# Shared Datasets for Python Labs

This directory contains datasets for introductory Python programming labs using pandas and data analysis.

## Available Datasets

### 1. iris.csv (~5 KB)
**Description:** Classic iris flower dataset with 150 samples
**Columns:**
- `sepal_length`: Sepal length in cm
- `sepal_width`: Sepal width in cm
- `petal_length`: Petal length in cm
- `petal_width`: Petal width in cm
- `species`: Flower species (setosa, versicolor, virginica)

**Use cases:** Basic pandas operations, groupby, filtering, visualization (scatter plots, histograms)

**Example usage:**
```python
import pandas as pd
df = pd.read_csv('/home/jovyan/shared-data/iris.csv')
df.groupby('species').mean()
```

### 2. sales_sample.csv (~2 KB)
**Description:** Sample sales data for e-commerce products
**Columns:**
- `date`: Sale date
- `product`: Product name
- `category`: Product category (Electronics, Accessories)
- `quantity`: Units sold
- `price`: Unit price
- `region`: Sales region (North, South, East, West)

**Use cases:** Aggregations, groupby operations, time series basics, revenue calculations

**Example usage:**
```python
import pandas as pd
df = pd.read_csv('/home/jovyan/shared-data/sales_sample.csv')
df['revenue'] = df['quantity'] * df['price']
df.groupby('region')['revenue'].sum()
```

### 3. student_grades.csv (~1 KB)
**Description:** Student grades across multiple subjects
**Columns:**
- `student_id`: Unique student identifier
- `name`: Student name
- `math`: Math grade (0-100)
- `physics`: Physics grade (0-100)
- `chemistry`: Chemistry grade (0-100)
- `programming`: Programming grade (0-100)
- `english`: English grade (0-100)

**Use cases:** Statistical analysis, correlations, mean/median/std calculations, grade distributions

**Example usage:**
```python
import pandas as pd
df = pd.read_csv('/home/jovyan/shared-data/student_grades.csv')
df[['math', 'physics', 'chemistry', 'programming', 'english']].mean()
df[['math', 'programming']].corr()
```

## Dataset Sizes
- **iris.csv:** ~5 KB (150 rows)
- **sales_sample.csv:** ~2 KB (36 rows)
- **student_grades.csv:** ~1 KB (30 rows)
- **Total:** ~8 KB

## Storage Efficiency
These datasets are stored once in shared read-only storage and mounted to all student pods at `/home/jovyan/shared-data/`. 

For 50 students:
- **Without deduplication:** 50 × 8 KB = 400 KB
- **With deduplication:** 1 × 8 KB = 8 KB
- **Space saved:** 392 KB (98% reduction)

## Important Notes
- All datasets are mounted **read-only** at `/home/jovyan/shared-data/`
- Students cannot modify these files
- To work with the data, students should load it into pandas DataFrames
- For modified versions, students should save to their personal workspace (`/home/jovyan/`)
