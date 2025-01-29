import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import os

# Carregar o arquivo CSV (substitua 'path_to_your_file.csv' pelo caminho do seu arquivo)
my_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(my_dir, "../../assets/images/")
csv_file = my_dir + "/latencies.csv"
data = pd.read_csv(csv_file)

# Só pra não esquecer :)
columns = ['msg_count', 'ind_latency', 'recv_latency',
           'class_latency', 'alloc_latency', 'tot_latency']

fig1 = plt.figure(figsize=(21, 12))
gs = fig1.add_gridspec(2, 2)
axs = [
    fig1.add_subplot(gs[0, 0]),
    fig1.add_subplot(gs[0, 1]),
    fig1.add_subplot(gs[1, 0]),
    fig1.add_subplot(gs[1, 1]),
]

# GRAFICO 1
axs[0].plot(data['msg_count'].iloc[2::100], data['ind_latency'].iloc[2::100],
            label="Latência de Reporte (ms)", alpha=0.8, color="green")
axs[0].set_title('Latência de Reporte', fontsize=20,
                 fontweight='bold', color='black', pad=20)
axs[0].set_xlabel(r'Nº mensagem $\times$ 10$^3$',
                  fontsize=15, labelpad=10)
axs[0].set_ylabel('Latência (ms)',
                  fontsize=15, labelpad=10)
axs[0].autoscale(enable=True, axis='both', tight=False)
# Configurar os ticks do eixo X em incrementos de 1000
axs[0].xaxis.set_major_locator(
    ticker.MultipleLocator(1000))  # Ticks a cada 1000
axs[0].xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x / 1e3)}'  # Formatar valores como '1k', '2k', etc.
))
axs[0].grid(alpha=0.5)
# axs[0].legend()

# GRAFICO 2
axs[1].plot(data['msg_count'][2::100], data['recv_latency'][2::100],
            label="Latência servidor de métricas (ms)", alpha=0.8, color="royalblue")
axs[1].set_title('Latência do Servidor de Métricas', fontsize=20,
                 fontweight='bold', color='black', pad=20)
axs[1].set_xlabel(r'Nº mensagem $\times$ 10$^3$',
                  fontsize=15, labelpad=10)
axs[1].set_ylabel('Latência (ms)',
                  fontsize=15, labelpad=10)
axs[1].autoscale(enable=True, axis='both', tight=False)
# Configurar os ticks do eixo X em incrementos de 1000
axs[1].xaxis.set_major_locator(
    ticker.MultipleLocator(1000))  # Ticks a cada 1000
axs[1].xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x / 1e3)}'  # Formatar valores como '1k', '2k', etc.
))
axs[1].yaxis.set_major_locator(ticker.MultipleLocator(0.3))
axs[1].grid(alpha=0.5)
# axs[1].legend()

# GRAFICO 3
axs[2].plot(data['msg_count'][2::100], data['class_latency'][2::100],
            label="Latência (ms)", alpha=0.8, color="goldenrod")
axs[2].set_title('Latência de Classificação', fontsize=20,
                 fontweight='bold', color='black', pad=20)
axs[2].set_xlabel(r'Nº mensagem $\times$ 10$^3$',
                  fontsize=15, labelpad=10)
axs[2].set_ylabel('Latência (ms)',
                  fontsize=15, labelpad=10)
axs[2].autoscale(enable=True, axis='both', tight=False)
# Co2figurar os ticks do eixo X em incrementos de 1000
axs[2].xaxis.set_major_locator(
    ticker.MultipleLocator(1000))  # Ticks a cada 1000
axs[2].xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x / 1e3)}'
))
axs[2].yaxis.set_major_locator(ticker.MultipleLocator(2.5))
axs[2].grid(alpha=0.5)

# GRAFICO 4
axs[3].plot(data['msg_count'][2::100], data['alloc_latency'][2::100],
            label="Latência inferência (ms)", alpha=0.8, color="indigo")
axs[3].set_title('Latência de Inferência/Alocação', fontsize=20,
                 fontweight='bold', color='black', pad=20)
axs[3].set_xlabel(r'Nº mensagem $\times$ 10$^3$',
                  fontsize=15, labelpad=10)
axs[3].set_ylabel('Latência (ms)',
                  fontsize=15, labelpad=10)
axs[3].autoscale(enable=True, axis='both', tight=False)
# Co2figurar os ticks do eixo X em incrementos de 1000
axs[3].xaxis.set_major_locator(
    ticker.MultipleLocator(1000))  # Ticks a cada 1000
axs[3].xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x / 1e3)}'
))
axs[3].yaxis.set_major_locator(ticker.MultipleLocator(0.2))
axs[3].grid(alpha=0.5)

plt.tight_layout(pad=3.0)

fig1.savefig(save_path + "latencies.pdf",
             format="pdf", dpi=1200)


# GRAFICO 5 -> Latência Total
fig2, ax = plt.subplots(figsize=(21, 12))

# Plotar Latência Total no eixo 'ax'
ax.plot(data['msg_count'][2::100], data['tot_latency'][2::100],
        label="Latência Total (ms)", alpha=0.8, color="sienna")

# Ajustar título e rótulos
ax.set_title('Latência Total', fontsize=20,
             fontweight='bold', color='black', pad=20)
ax.set_xlabel(r'Nº mensagem $\times$ 10$^3$',
              fontsize=15, labelpad=10)
ax.set_ylabel('Latência Total (ms)',
              fontsize=15, labelpad=10)

# Ajustar os ticks do eixo X e Y
ax.autoscale(enable=True, axis='both')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1000))  # Ticks a cada 1000
ax.xaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f'{int(x / 1e3)}'))  # Formatar valores como '1k', '2k', etc.
# Ajuste da escala no eixo Y
ax.yaxis.set_major_locator(ticker.MultipleLocator(1.5))

# Configurar grid
ax.grid(alpha=0.5)

# Adicionar legenda
# ax.legend()  # Posição da legenda

# Salvar gráficos
fig2.savefig(save_path + "tot_latency.pdf",
             format="pdf", dpi=1200)

# Exibir o gráfico
plt.show()
