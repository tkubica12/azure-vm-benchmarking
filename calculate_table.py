import pandas as pd
import yaml

# Load YAML data
with open('results.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Convert YAML to DataFrame
vms = data['vms']
df = pd.DataFrame.from_dict(vms, orient='index').reset_index()
df.rename(columns={
    'index': 'index',
    'sku_name': 'sku',
    'cpu_name': 'cpu',
    'price_hour': 'price_hour',
    'price_hour_3y_ri': 'price_hour_3y_ri',
    'nginx': 'nginx',
    'redis': 'redis',
    'stockfish': 'stockfish'
}, inplace=True)

# Recalculate prices to per month (730 hours per month) and round to one decimal place
df['price_month'] = (df['price_hour'] * 730).round(1)
df['price_month_3y_ri'] = (df['price_hour_3y_ri'] * 730).round(1)

# Remove the original per-hour price columns
df.drop(['price_hour', 'price_hour_3y_ri'], axis=1, inplace=True)

# Calculate Relative Performance (Higher is better)
tests = ['nginx', 'redis', 'stockfish']
for test in tests:
    min_val = df[test].min()
    df[f'{test}_score'] = (df[test] / min_val * 100).round(1)

# Calculate Price per Score Performance (Scaled)
# At score=100, price_scaled = price_month
# If score > 100, price_scaled = price_month * 100 / score (lower price for better performance)
price_types = ['price_month', 'price_month_3y_ri']
for price in price_types:
    for test in tests:
        ppsp_column = f'{test}_ppsp_{price}'
        df[ppsp_column] = (df[price] * 100 / df[f'{test}_score']).round(1)

# Reorder Columns: sku, cpu, prices, then for each test: test, score, price per score
desired_columns = ['sku', 'cpu', 'price_month', 'price_month_3y_ri']
for test in tests:
    desired_columns.extend([
        test,
        f'{test}_score',
        f'{test}_ppsp_price_month',
        f'{test}_ppsp_price_month_3y_ri'
    ])

df = df[desired_columns]

# Function to generate HTML table with grouped headers and highlighting
def generate_grouped_html_table(df, tests):
    # Define which columns are higher or lower better
    higher_better_columns = ['nginx', 'redis', 'stockfish', 
                             'nginx_score', 'redis_score', 'stockfish_score']
    lower_better_columns = ['price_month', 'price_month_3y_ri',
                            'nginx_ppsp_price_month', 'nginx_ppsp_price_month_3y_ri',
                            'redis_ppsp_price_month', 'redis_ppsp_price_month_3y_ri',
                            'stockfish_ppsp_price_month', 'stockfish_ppsp_price_month_3y_ri']
    
    # Calculate min and max for each relevant column
    min_values_lower = df[lower_better_columns].min()
    max_values_lower = df[lower_better_columns].max()
    min_values_higher = df[higher_better_columns].min()
    max_values_higher = df[higher_better_columns].max()
    
    # Combine min and max values
    min_values = pd.concat([min_values_lower, min_values_higher])
    max_values = pd.concat([max_values_lower, max_values_higher])
    
    html = '<table style="border-collapse: collapse; width: 100%;">\n'
    
    # First header row with grouped test names
    html += '  <tr>\n'
    html += '    <th rowspan="2" style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">SKU</th>\n'
    html += '    <th rowspan="2" style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">CPU</th>\n'
    html += '    <th rowspan="2" style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Price (Monthly)</th>\n'
    html += '    <th rowspan="2" style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Price (Monthly 3Y RI)</th>\n'
    for test in tests:
        html += f'    <th colspan="4" style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">{test.capitalize()}</th>\n'
    html += '  </tr>\n'
    
    # Second header row with specific test metrics
    html += '  <tr>\n'
    for test in tests:
        html += '    <th style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Performance</th>\n'
        html += '    <th style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Score</th>\n'
        html += '    <th style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Price per Score (Monthly)</th>\n'
        html += '    <th style="background-color: #4CAF50; color: white; border: 1px solid #ddd; padding: 8px;">Price per Score (Monthly 3Y RI)</th>\n'
    html += '  </tr>\n'
    
    # Data rows with highlighting for best and worst
    for index, row in df.iterrows():
        bg_color = "#f2f2f2" if index % 2 == 1 else "white"
        html += f'  <tr style="background-color: {bg_color};">\n'
        html += f'    <td style="border: 1px solid #ddd; padding: 8px;"><strong>{row["sku"]}</strong></td>\n'
        html += f'    <td style="border: 1px solid #ddd; padding: 8px;">{row["cpu"]}</td>\n'
        html += f'    <td style="border: 1px solid #ddd; padding: 8px;">{row["price_month"]}</td>\n'
        html += f'    <td style="border: 1px solid #ddd; padding: 8px;">{row["price_month_3y_ri"]}</td>\n'
        for test in tests:
            # Performance
            perf = row[test]
            if perf == df[test].max():
                perf_style = 'background-color: #e6f4ea;'  # Lighter green
            elif perf == df[test].min():
                perf_style = 'background-color: #fdecea;'  # Lighter red
            else:
                perf_style = ''
            html += f'    <td style="border: 1px solid #ddd; padding: 8px; {perf_style}">{perf}</td>\n'
            
            # Score
            score = row[f"{test}_score"]
            if score == df[f"{test}_score"].max():
                score_style = 'background-color: #e6f4ea;'  # Lighter green
            elif score == df[f"{test}_score"].min():
                score_style = 'background-color: #fdecea;'  # Lighter red
            else:
                score_style = ''
            html += f'    <td style="border: 1px solid #ddd; padding: 8px; {score_style}">{score}</td>\n'
            
            # Price per Score (Monthly)
            ppsp_month = row[f"{test}_ppsp_price_month"]
            if ppsp_month == df[f"{test}_ppsp_price_month"].min():
                ppsp_month_style = 'background-color: #e6f4ea;'  # Lighter green
            elif ppsp_month == df[f"{test}_ppsp_price_month"].max():
                ppsp_month_style = 'background-color: #fdecea;'  # Lighter red
            else:
                ppsp_month_style = ''
            html += f'    <td style="border: 1px solid #ddd; padding: 8px; {ppsp_month_style}">{ppsp_month}</td>\n'
            
            # Price per Score (Monthly 3Y RI)
            ppsp_3y = row[f"{test}_ppsp_price_month_3y_ri"]
            if ppsp_3y == df[f"{test}_ppsp_price_month_3y_ri"].min():
                ppsp_3y_style = 'background-color: #e6f4ea;'  # Lighter green
            elif ppsp_3y == df[f"{test}_ppsp_price_month_3y_ri"].max():
                ppsp_3y_style = 'background-color: #fdecea;'  # Lighter red
            else:
                ppsp_3y_style = ''
            html += f'    <td style="border: 1px solid #ddd; padding: 8px; {ppsp_3y_style}">{ppsp_3y}</td>\n'
        html += '  </tr>\n'
    
    html += '</table>'
    return html

# Generate the HTML table
html_table = generate_grouped_html_table(df, tests)

# Store table as Markdown file with embedded HTML
with open('docs/results_table.html', 'w') as md_file:
    md_file.write(html_table)