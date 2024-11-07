import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('app/data/latency_data.csv')

plt.figure(figsize=(10, 6))

plt.plot(data['msg_counter'], data['latency_ms'], marker='o', linestyle='-', color='b')

# plt.title('Latency vs Processed Indication', fontsize=16)
plt.xlabel('Message Count', fontsize=14)
plt.ylabel('Latency (ms)', fontsize=14)

# plt.xticks(data['msg_counter'])  # Define os rótulos do eixo x com os contadores de mensagem
plt.grid()

plt.show()