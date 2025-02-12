import os
import matplotlib.pyplot as plt
import numpy as np

def parse_log_file(file_path):
    buffer_utilizations = []
    memory_bandwidths = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 10:
                continue
            
            mmu_num = int(parts[1])
            
            if 0 <= mmu_num < 4:
                buffer_utilizations.append(float(parts[2 + mmu_num]) * 100)
                memory_bandwidths.append(float(parts[6 + mmu_num]) / 8e11 * 100)

    return buffer_utilizations, memory_bandwidths

def plot_cdf(data, label, linestyle, color):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf, label=label, linestyle=linestyle, color=color)

def process_logs(folder, alpha_values, web_loads):
    for web_load in web_loads:
        plt.figure(figsize=(8, 6))
        for alpha in alpha_values:
            buffer_utilizations = []
            for sw in range(16):
                file_name = f"DT-{alpha}~DCTCP-{web_load}-0.0-200.0-4194304-2-q-sw-{sw}.txt"
                file_path = os.path.join(folder, file_name)
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue
                
                buf_util, _ = parse_log_file(file_path)
                buffer_utilizations.extend(buf_util) 
            
            if buffer_utilizations:
                label = f"α = {alpha}"
                color = 'red' if alpha == '0.5' else 'green' 
                linestyle = '-' if alpha == '0.5' else '--'
                plot_cdf(buffer_utilizations, label=label, linestyle=linestyle, color=color)

        plt.xlabel("Utilization (%)")
        plt.ylabel("CDF")
        plt.xlim(0, 100)
        plt.title(f"Buffer Utilization (Load = {float(web_load) * 100:.0f}%)")
        plt.legend()
        plt.grid(True)

        save_folder = "figure/utilization"
        os.makedirs(save_folder, exist_ok=True)
        plt.savefig(f"{save_folder}/buffer_utilization_load_{float(web_load) * 100:.0f}.png", dpi=300)
        plt.close()

    for alpha in alpha_values:
        plt.figure(figsize=(8, 6))
        for web_load in web_loads:
            memory_bandwidths = [] 
            for sw in range(16):
                file_name = f"DT-{alpha}~DCTCP-{web_load}-0.0-200.0-4194304-2-q-sw-{sw}.txt"
                file_path = os.path.join(folder, file_name)
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue

                _, mem_band = parse_log_file(file_path)
                memory_bandwidths.extend(mem_band) 
            
            if memory_bandwidths:
                label = f"Load = {float(web_load) * 100:.0f}%"
                color = 'red' if web_load == '0.2' else ('green' if web_load == '0.4' else 'blue') 
                linestyle = '-' if web_load == '0.2' else ('--' if web_load == '0.4' else ':')
                plot_cdf(memory_bandwidths, label=label, linestyle=linestyle, color=color)

        plt.xlabel("Utilization (%)")
        plt.ylabel("CDF")
        plt.xlim(0, 100)
        plt.title(f"Memory Bandwidth (α = {alpha})")
        plt.legend()
        plt.grid(True)

        save_folder = "figure/utilization"
        os.makedirs(save_folder, exist_ok=True)
        plt.savefig(f"{save_folder}/memory_bandwidth_alpha_{alpha}.png", dpi=300)
        plt.close()


if __name__ == "__main__":
    log_folder = "log_utilization/"
    alpha_values = ["0.5", "1.0"]
    web_loads = ["0.2", "0.4", "0.9"]

    process_logs(log_folder, alpha_values, web_loads)
