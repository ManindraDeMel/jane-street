import pandas as pd
import matplotlib.pyplot as plt

# Load the data
data = pd.read_csv('best_bid_ask.csv', names=['Timestamp', 'Best Bid', 'Best Ask'], parse_dates=['Timestamp'])

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(data['Timestamp'], data['Best Bid'], label='Best Bid')
plt.plot(data['Timestamp'], data['Best Ask'], label='Best Ask')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.title('Best Bid and Ask Over Time')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
