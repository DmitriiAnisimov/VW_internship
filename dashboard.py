import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

# Чтение файлов CSV в DataFrame
features = pd.read_csv('features.csv')
predictions = pd.read_csv('predictions.csv')

# Убедитесь, что временные метки имеют тип datetime
features['timestamp'] = pd.to_datetime(features['timestamp'])
predictions['timestamp'] = pd.to_datetime(predictions['timestamp'])

# Проверка столбцов после преобразования
print("Features columns after conversion:", features.columns)
print("Predictions columns after conversion:", predictions.columns)

# Используем значение с индексом 1 для прогноза
if 1 in predictions.index:
    avg_orders_next_hour = predictions.loc[1, 'orders']
else:
    avg_orders_next_hour = predictions['orders'].mean()
    print("Index 1 not found in predictions DataFrame. Using average value.")

# Последняя строка текущих данных
last_row = features[['orders', 'timestamp']].iloc[[-1]]
predictions = pd.concat([last_row, predictions], ignore_index=True)

# Пример данных для текущих заказов
current_data = features[24*7:]

# Последнее значение временной метки текущих данных
last_timestamp = current_data['timestamp'].max()

# Разница между последним временным штампом текущих данных и минимальным временным штампом предсказаний
time_shift = last_timestamp - predictions['timestamp'].min()

# Устанавливаем первую точку предсказания на следующую после последней точки текущих данных
predictions['timestamp'] = predictions['timestamp'] + time_shift

# Объединение данных
combined_data = pd.concat([current_data, predictions]).reset_index(drop=True)

# Пример данных о заполненности ячеек
total_cells = 100
filled_cells = 71
empty_cells = total_cells - filled_cells

# Рассчитываем время до переполнения
time_to_fill = empty_cells / avg_orders_next_hour  # Время до переполнения в часах

# Преобразование времени до переполнения в удобный формат
hours, minutes = divmod(time_to_fill * 60, 60)
formatted_time_to_fill = f"{int(hours)} ч {int(minutes)} мин"

# Вычисляем процент заполненности
percentage_filled = filled_cells / total_cells

# Создание данных о заполненности ячеек
cell_status = []
for i in range(total_cells):
    if i < filled_cells:
        if percentage_filled >= 0.70:
            color = 'red'
        elif percentage_filled >= 0.60:
            color = 'orange'
        else:
            color = 'green'
    else:
        color = 'grey'
    cell_status.append(color)

cell_data = pd.DataFrame({
    'Ячейка': range(total_cells),
    'Состояние': cell_status
})

# Преобразование данных для отображения в виде графика
cell_data['Ряд'] = (cell_data.index // 10) + 1
cell_data['Колонка'] = cell_data.index % 10

# Создание графика
fig_cells = go.Figure()

# Добавление ячеек в график
for row in cell_data['Ряд'].unique():
    row_data = cell_data[cell_data['Ряд'] == row]
    fig_cells.add_trace(go.Scatter(
        x=row_data['Колонка'],
        y=[row] * len(row_data),
        mode='markers',
        marker=dict(size=20, color=row_data['Состояние'].map({'red': 'red', 'orange': 'orange', 'green': 'green', 'grey': 'grey'})),
        name=f'Ряд {row}',
        text=row_data['Состояние'],
        textposition='top center'
    ))

# Инициализируйте приложение Dash
app = dash.Dash(__name__)

# Определите макет дашборда
app.layout = html.Div([
    html.Div([
        html.H1("График заказов и предсказаний"),
        dcc.Graph(
            id='orders-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=current_data['timestamp'],
                        y=current_data['orders'],
                        mode='lines+markers',
                        name='Текущие заказы',
                        line=dict(color='blue')
                    ),
                    go.Scatter(
                        x=predictions['timestamp'],
                        y=predictions['orders'],
                        mode='lines+markers',
                        name='Предсказания',
                        line=dict(color='red')
                    )
                ],
                'layout': go.Layout(
                    title='График текущих заказов и предсказаний',
                    titlefont={'size': 40},  # Увеличено название графика
                    xaxis={'title': 'Время', 'titlefont': {'size': 32}, 'tickfont': {'size': 24}},
                    yaxis={'title': 'Количество заказов', 'titlefont': {'size': 32}, 'tickfont': {'size': 24}},
                    legend={'font': {'size': 36}},  # Увеличен размер шрифта легенды
                )
            }
        )
    ], style={'padding': '36px'}),

    html.Div([
        html.H1("Время до переполнения"),
        html.P(f"Прогнозируемое количество заказов на следующий час: {avg_orders_next_hour:.0f}", style={'fontSize': '32px'}),
        html.P(f"Время до переполнения: {formatted_time_to_fill}", style={'fontSize': '32px'})
    ], style={'padding': '40px'}),

    html.Div([
        html.H2("Заполненность ячеек даркстора"),
        dcc.Graph(
            id='storage-graph',
            figure={
                'data': fig_cells.data,
                'layout': go.Layout(
                    title='Заполненность ячеек даркстора',
                    titlefont={'size': 40},  # Увеличено название графика
                    xaxis={'title': 'Ячейка', 'titlefont': {'size': 32}, 'tickfont': {'size': 24}},
                    yaxis={'title': 'Ряд', 'titlefont': {'size': 32}, 'tickfont': {'size': 24}},
                    showlegend=False
                )
            }
        )
    ], style={'padding': '36px'})
], style={'display': 'flex', 'flexDirection': 'column', 'fontSize': '32px'})

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
