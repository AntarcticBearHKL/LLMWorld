import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter as tk
from tkinter import ttk

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class TabbedEnergyVisualizer:
    def __init__(self):
        self.output_dir = "output"
        self.available_runs = self._scan_available_runs()
        self.selected_run_id = None
        self.selected_dates = []
        
    def _scan_available_runs(self):
        runs = {}
        if not os.path.exists(self.output_dir):
            return runs
        
        for run_folder in os.listdir(self.output_dir):
            run_path = os.path.join(self.output_dir, run_folder)
            if not os.path.isdir(run_path) or not run_folder.endswith("_logs"):
                continue
            
            run_id = run_folder.replace("_logs", "")
            dates = []
            
            for date_folder in os.listdir(run_path):
                date_path = os.path.join(run_path, date_folder)
                energy_info_path = os.path.join(date_path, "用电信息")
                
                if os.path.isdir(energy_info_path):
                    summary_file = os.path.join(energy_info_path, "总用电汇总.json")
                    if os.path.exists(summary_file):
                        dates.append(date_folder)
            
            if dates:
                runs[run_id] = sorted(dates)
        
        return runs
    
    def select_run_and_dates(self):
        if not self.available_runs:
            print("未找到任何用电数据")
            return False
        
        root = tk.Tk()
        root.title("选择运行ID和日期")
        root.geometry("500x400")
        
        selected_run = tk.StringVar()
        
        ttk.Label(root, text="选择运行ID:", font=("Arial", 12)).pack(pady=10)
        run_combo = ttk.Combobox(root, textvariable=selected_run, width=40, font=("Arial", 10))
        run_combo['values'] = list(self.available_runs.keys())
        run_combo.pack(pady=5)
        
        ttk.Label(root, text="选择日期 (可多选):", font=("Arial", 12)).pack(pady=10)
        
        listbox_frame = tk.Frame(root)
        listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        date_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, 
                                   yscrollcommand=scrollbar.set, font=("Arial", 10))
        date_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=date_listbox.yview)
        
        def on_run_selected(event):
            run_id = selected_run.get()
            if run_id in self.available_runs:
                date_listbox.delete(0, tk.END)
                for date in self.available_runs[run_id]:
                    date_listbox.insert(tk.END, date)
        
        run_combo.bind('<<ComboboxSelected>>', on_run_selected)
        
        if self.available_runs:
            run_combo.current(0)
            first_run = list(self.available_runs.keys())[0]
            for date in self.available_runs[first_run]:
                date_listbox.insert(tk.END, date)
        
        def on_confirm():
            self.selected_run_id = selected_run.get()
            selected_indices = date_listbox.curselection()
            self.selected_dates = [date_listbox.get(i) for i in selected_indices]
            root.quit()
            root.destroy()
        
        ttk.Button(root, text="确认", command=on_confirm).pack(pady=20)
        
        root.mainloop()
        
        return self.selected_run_id and self.selected_dates
    
    def load_energy_data(self, date):
        energy_info_dir = os.path.join(
            self.output_dir,
            f"{self.selected_run_id}_logs",
            date,
            "用电信息"
        )
        
        summary_file = os.path.join(energy_info_dir, "总用电汇总.json")
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
        
        appliance_details = {}
        for filename in os.listdir(energy_info_dir):
            if filename.endswith(".json") and filename != "总用电汇总.json":
                filepath = os.path.join(energy_info_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    appliance_data = json.load(f)
                    unique_id = appliance_data["appliance_info"]["unique_id"]
                    appliance_details[unique_id] = appliance_data
        
        return summary_data, appliance_details
    
    def create_tabbed_window(self):
        root = tk.Tk()
        root.title(f'用电数据分析 - 运行ID: {self.selected_run_id}')
        root.state('zoomed')
        
        def on_closing():
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if len(self.selected_dates) == 1:
            self._create_single_day_tabs(notebook, self.selected_dates[0])
        else:
            self._create_multi_day_tabs(notebook)
        
        root.mainloop()
        plt.close('all')
    
    def _create_single_day_tabs(self, notebook, date):
        summary_data, appliance_details = self.load_energy_data(date)
        
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text='电器用电量排行')
        self._create_tab_chart(tab1, lambda ax: self._plot_energy_bar(ax, summary_data, date))
        
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text='电器使用时间线')
        self._create_tab_chart(tab2, lambda ax: self._plot_timeline_all(ax, appliance_details, date))
        
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text='24小时用电分布')
        self._create_tab_chart(tab3, lambda ax: self._plot_hourly_distribution(ax, appliance_details, date))
        
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text='电器使用时长排行')
        self._create_tab_chart(tab4, lambda ax: self._plot_usage_hours(ax, summary_data, date))
        
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text='按电器类型统计')
        self._create_tab_chart(tab5, lambda ax: self._plot_appliance_type_summary(ax, appliance_details, date))
    
    def _create_multi_day_tabs(self, notebook):
        all_data = {}
        for date in self.selected_dates:
            summary_data, appliance_details = self.load_energy_data(date)
            all_data[date] = {
                'summary': summary_data,
                'details': appliance_details
            }
        
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text='每日总用电量对比')
        self._create_tab_chart(tab1, lambda ax: self._plot_daily_total_comparison(ax, all_data))
        
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text='主要电器用电趋势')
        self._create_tab_chart(tab2, lambda ax: self._plot_appliance_trend(ax, all_data))
        
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text='每日平均使用时长')
        self._create_tab_chart(tab3, lambda ax: self._plot_daily_usage_hours(ax, all_data))
        
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text='每日用电峰值时段')
        self._create_tab_chart(tab4, lambda ax: self._plot_peak_hours_comparison(ax, all_data))
        
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text='用电效率分析')
        self._create_tab_chart(tab5, lambda ax: self._plot_efficiency_analysis(ax, all_data))
        
        tab6 = ttk.Frame(notebook)
        notebook.add(tab6, text='各日24小时对比')
        self._create_tab_chart(tab6, lambda ax: self._plot_multi_day_hourly(ax, all_data))
    
    def _create_tab_chart(self, parent, plot_function):
        fig, ax = plt.subplots(figsize=(14, 8))
        plot_function(ax)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _plot_energy_bar(self, ax, summary_data, date):
        appliances = sorted(summary_data["appliances"], 
                           key=lambda x: x["total_energy_kwh"], 
                           reverse=True)[:15]
        
        names = [a["name"] for a in appliances]
        energies = [a["total_energy_kwh"] for a in appliances]
        
        bars = ax.barh(names, energies, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(names))))
        
        for i, (bar, energy) in enumerate(zip(bars, energies)):
            ax.text(energy, i, f' {energy:.2f} kWh', 
                   va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title(f'电器用电量排行 (Top 15) - {date}\n总用电量: {summary_data["total_energy_kwh"]:.2f} kWh', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_timeline_all(self, ax, appliance_details, date):
        appliances = sorted(appliance_details.items(), 
                           key=lambda x: x[1]["usage_summary"]["total_energy_kwh"],
                           reverse=True)[:20]
        
        y_labels = []
        y_positions = []
        
        for idx, (unique_id, data) in enumerate(appliances):
            name = data["appliance_info"]["name"]
            energy = data["usage_summary"]["total_energy_kwh"]
            hours = data["usage_summary"]["total_hours"]
            y_labels.append(f'{name} ({energy:.2f}kWh, {hours:.1f}h)')
            y_positions.append(idx)
            
            for segment in data["usage_segments"]:
                start = segment["start_minutes"]
                end = segment["end_minutes"]
                
                if end > 1440:
                    ax.barh(idx, 1440 - start, left=start/60, height=0.8, 
                           color=plt.cm.tab20(idx % 20), alpha=0.7, edgecolor='black', linewidth=0.5)
                    ax.barh(idx, end - 1440, left=0, height=0.8,
                           color=plt.cm.tab20(idx % 20), alpha=0.7, edgecolor='black', linewidth=0.5)
                else:
                    ax.barh(idx, (end - start)/60, left=start/60, height=0.8,
                           color=plt.cm.tab20(idx % 20), alpha=0.7, edgecolor='black', linewidth=0.5)
        
        ax.set_yticks(y_positions)
        ax.set_yticklabels(y_labels, fontsize=10)
        ax.set_xlabel('时间 (小时)', fontsize=14, fontweight='bold')
        ax.set_title(f'电器使用时间线 (Top 20) - {date}', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim(0, 24)
        ax.set_xticks(range(0, 25, 1))
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
        ax.tick_params(axis='x', labelsize=11)
    
    def _plot_hourly_distribution(self, ax, appliance_details, date):
        hourly_energy = [0] * 24
        
        for unique_id, data in appliance_details.items():
            power_watts = data["appliance_info"]["power_watts"]
            
            for segment in data["usage_segments"]:
                start = segment["start_minutes"]
                end = segment["end_minutes"]
                
                for minute in range(start, end):
                    actual_minute = minute % 1440
                    hour = actual_minute // 60
                    hourly_energy[hour] += power_watts / 60000.0
        
        hours = range(24)
        bars = ax.bar(hours, hourly_energy, color=plt.cm.plasma(np.linspace(0.2, 0.9, 24)), 
                      edgecolor='black', linewidth=1)
        
        for bar, energy in zip(bars, hourly_energy):
            height = bar.get_height()
            if energy > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{energy:.2f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        peak_hour = hourly_energy.index(max(hourly_energy))
        peak_energy = max(hourly_energy)
        
        ax.set_xlabel('小时', fontsize=14, fontweight='bold')
        ax.set_ylabel('用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title(f'24小时用电分布 - {date}\n峰值时段: {peak_hour}:00 ({peak_energy:.2f} kWh)', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(range(0, 24))
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_usage_hours(self, ax, summary_data, date):
        appliances = sorted(summary_data["appliances"],
                           key=lambda x: x["total_hours"],
                           reverse=True)[:15]
        
        names = [a["name"] for a in appliances]
        hours = [a["total_hours"] for a in appliances]
        
        bars = ax.barh(names, hours, color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(names))))
        
        for i, (bar, hour) in enumerate(zip(bars, hours)):
            ax.text(hour, i, f' {hour:.1f}h',
                   va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('使用时长 (小时)', fontsize=14, fontweight='bold')
        ax.set_title(f'电器使用时长排行 (Top 15) - {date}', fontsize=16, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_appliance_type_summary(self, ax, appliance_details, date):
        type_energy = {}
        type_count = {}
        
        for unique_id, data in appliance_details.items():
            appliance_type = data["appliance_info"]["type"]
            energy = data["usage_summary"]["total_energy_kwh"]
            
            if appliance_type not in type_energy:
                type_energy[appliance_type] = 0
                type_count[appliance_type] = 0
            type_energy[appliance_type] += energy
            type_count[appliance_type] += 1
        
        type_names = {'on_demand': '按需使用', 'charging': '充电设备', 'always_on': '持续运行'}
        types = [type_names.get(t, t) for t in type_energy.keys()]
        energies = list(type_energy.values())
        counts = list(type_count.values())
        
        colors = {'按需使用': '#FF6B6B', '充电设备': '#4ECDC4', '持续运行': '#95E1D3'}
        bar_colors = [colors.get(t, '#CCCCCC') for t in types]
        
        x = np.arange(len(types))
        width = 0.6
        bars = ax.bar(x, energies, width, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=2)
        
        for i, (bar, energy, count) in enumerate(zip(bars, energies, counts)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{energy:.2f} kWh\n({count}个电器)',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(types, fontsize=12)
        ax.set_ylabel('用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title(f'按电器类型统计 - {date}', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_daily_total_comparison(self, ax, all_data):
        dates = list(all_data.keys())
        totals = [all_data[date]['summary']['total_energy_kwh'] for date in dates]
        
        bars = ax.bar(range(len(dates)), totals, 
                      color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(dates))),
                      edgecolor='black', linewidth=2)
        
        for i, (bar, total) in enumerate(zip(bars, totals)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{total:.2f} kWh',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        avg_total = np.mean(totals)
        ax.axhline(y=avg_total, color='red', linestyle='--', linewidth=2, label=f'平均值: {avg_total:.2f} kWh')
        
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('总用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title('每日总用电量对比', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(fontsize=11)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_appliance_trend(self, ax, all_data):
        all_appliances = set()
        for date, data in all_data.items():
            for appliance in data['summary']['appliances']:
                all_appliances.add(appliance['name'])
        
        top_appliances = []
        for appliance_name in all_appliances:
            total = sum(
                next((a['total_energy_kwh'] for a in data['summary']['appliances'] 
                      if a['name'] == appliance_name), 0)
                for data in all_data.values()
            )
            top_appliances.append((appliance_name, total))
        
        top_appliances = sorted(top_appliances, key=lambda x: x[1], reverse=True)[:8]
        
        dates = list(all_data.keys())
        x = range(len(dates))
        
        for i, (appliance_name, _) in enumerate(top_appliances):
            energies = []
            for date in dates:
                energy = next(
                    (a['total_energy_kwh'] for a in all_data[date]['summary']['appliances']
                     if a['name'] == appliance_name), 0
                )
                energies.append(energy)
            
            ax.plot(x, energies, marker='o', label=appliance_name, linewidth=3, markersize=8)
        
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title('主要电器用电趋势 (Top 8)', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_daily_usage_hours(self, ax, all_data):
        dates = list(all_data.keys())
        avg_hours = []
        
        for date in dates:
            total_hours = sum(a['total_hours'] for a in all_data[date]['summary']['appliances'])
            avg_hours.append(total_hours / len(all_data[date]['summary']['appliances']))
        
        bars = ax.bar(range(len(dates)), avg_hours,
                      color=plt.cm.summer(np.linspace(0.3, 0.9, len(dates))),
                      edgecolor='black', linewidth=2)
        
        for i, (bar, hours) in enumerate(zip(bars, avg_hours)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{hours:.1f}h',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        avg_value = np.mean(avg_hours)
        ax.axhline(y=avg_value, color='red', linestyle='--', linewidth=2, label=f'平均值: {avg_value:.1f}h')
        
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('平均使用时长 (小时)', fontsize=14, fontweight='bold')
        ax.set_title('每日平均电器使用时长', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(fontsize=11)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_peak_hours_comparison(self, ax, all_data):
        dates = list(all_data.keys())
        peak_hours_data = []
        
        for date in dates:
            hourly_energy = [0] * 24
            
            for unique_id, data in all_data[date]['details'].items():
                power_watts = data["appliance_info"]["power_watts"]
                
                for segment in data["usage_segments"]:
                    start = segment["start_minutes"]
                    end = segment["end_minutes"]
                    
                    for minute in range(start, end):
                        actual_minute = minute % 1440
                        hour = actual_minute // 60
                        hourly_energy[hour] += power_watts / 60000.0
            
            peak_hour = hourly_energy.index(max(hourly_energy))
            peak_energy = max(hourly_energy)
            peak_hours_data.append((peak_hour, peak_energy))
        
        x = range(len(dates))
        peak_hours = [p[0] for p in peak_hours_data]
        peak_energies = [p[1] for p in peak_hours_data]
        
        bars = ax.bar(x, peak_energies, color=plt.cm.Reds(np.linspace(0.4, 0.9, len(dates))),
                      edgecolor='black', linewidth=2)
        
        for i, (bar, hour, energy) in enumerate(zip(bars, peak_hours, peak_energies)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{hour}:00\n{energy:.2f}kWh',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('峰值用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title('每日用电峰值时段', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_efficiency_analysis(self, ax, all_data):
        dates = list(all_data.keys())
        efficiency_scores = []
        
        for date in dates:
            total_energy = all_data[date]['summary']['total_energy_kwh']
            total_appliances = all_data[date]['summary']['total_appliances']
            avg_energy_per_appliance = total_energy / total_appliances if total_appliances > 0 else 0
            efficiency_scores.append(avg_energy_per_appliance)
        
        bars = ax.bar(range(len(dates)), efficiency_scores,
                      color=plt.cm.viridis(np.linspace(0.2, 0.8, len(dates))),
                      edgecolor='black', linewidth=2)
        
        for i, (bar, score) in enumerate(zip(bars, efficiency_scores)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.2f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        avg_score = np.mean(efficiency_scores)
        ax.axhline(y=avg_score, color='red', linestyle='--', linewidth=2, label=f'平均值: {avg_score:.2f}')
        
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('平均单电器用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title('用电效率分析', fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(fontsize=11)
        ax.tick_params(axis='both', labelsize=11)
    
    def _plot_multi_day_hourly(self, ax, all_data):
        dates = list(all_data.keys())
        
        for date in dates:
            hourly_energy = [0] * 24
            
            for unique_id, data in all_data[date]['details'].items():
                power_watts = data["appliance_info"]["power_watts"]
                
                for segment in data["usage_segments"]:
                    start = segment["start_minutes"]
                    end = segment["end_minutes"]
                    
                    for minute in range(start, end):
                        actual_minute = minute % 1440
                        hour = actual_minute // 60
                        hourly_energy[hour] += power_watts / 60000.0
            
            ax.plot(range(24), hourly_energy, marker='o', label=date, linewidth=3, markersize=6)
        
        ax.set_xlabel('小时', fontsize=14, fontweight='bold')
        ax.set_ylabel('用电量 (kWh)', fontsize=14, fontweight='bold')
        ax.set_title('各日24小时用电对比', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(range(0, 24))
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', labelsize=11)
    
    def run(self):
        if not self.select_run_and_dates():
            print("未选择数据")
            return
        
        print(f"正在加载数据: 运行ID={self.selected_run_id}")
        print(f"选择的日期: {', '.join(self.selected_dates)}")
        
        self.create_tabbed_window()

if __name__ == "__main__":
    visualizer = TabbedEnergyVisualizer()
    visualizer.run()
