# ui.py - 第一部分
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database
from models import Ledger, AssetRecord

class AccountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("资产盘点")
        self.root.geometry("1200x800")
        
        self.db = Database()
        
        self.setup_ui()
        self.create_menu()
        self.show_asset_management()  # 默认显示资产管理页面
        self.refresh_data()
    
    def create_menu(self):
        """创建顶部菜单"""
        self.menu_frame = ttk.Frame(self.root)
        self.menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 0))
        
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.columnconfigure(1, weight=1)
        
        # 资产管理按钮
        self.asset_mgmt_btn = ttk.Button(
            self.menu_frame, 
            text="资产管理", 
            command=self.show_asset_management
        )
        self.asset_mgmt_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        # 资产统计按钮
        self.asset_stats_btn = ttk.Button(
            self.menu_frame, 
            text="资产统计", 
            command=self.show_asset_statistics
        )
        self.asset_stats_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def setup_ui(self):
        """设置用户界面"""
        # 主内容框架
        self.content_frame = ttk.Frame(self.root, padding="10")
        self.content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # 创建资产管理页面
        self.create_asset_management_page()
        
        # 创建资产统计页面
        self.create_asset_statistics_page()
    
    def create_asset_management_page(self):
        """创建资产管理页面"""
        self.management_frame = ttk.Frame(self.content_frame)
        self.management_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.management_frame.columnconfigure(1, weight=1)
        self.management_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(self.management_frame, text="资产管理", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 创建账本管理区域
        ledger_frame = ttk.LabelFrame(self.management_frame, text="账本管理", padding="10")
        ledger_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        ttk.Label(ledger_frame, text="账本名称:").grid(row=0, column=0, sticky=tk.W)
        self.ledger_name_var = tk.StringVar()
        ttk.Entry(ledger_frame, textvariable=self.ledger_name_var, width=20).grid(row=0, column=1, pady=5)
        
        ttk.Label(ledger_frame, text="描述:").grid(row=1, column=0, sticky=tk.W)
        self.ledger_desc_var = tk.StringVar()
        ttk.Entry(ledger_frame, textvariable=self.ledger_desc_var, width=20).grid(row=1, column=1, pady=5)
        
        ttk.Button(ledger_frame, text="添加账本", command=self.add_ledger).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 账本列表
        ttk.Label(ledger_frame, text="现有账本:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.ledger_listbox = tk.Listbox(ledger_frame, height=8)
        self.ledger_listbox.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.ledger_listbox.bind('<<ListboxSelect>>', self.on_ledger_select)
        
        ttk.Button(ledger_frame, text="删除选中账本", command=self.delete_ledger).grid(row=5, column=0, columnspan=2, pady=5)
        
        # 资产记录区域
        record_frame = ttk.LabelFrame(self.management_frame, text="资产记录", padding="10")
        record_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(record_frame, text="选择账本:").grid(row=0, column=0, sticky=tk.W)
        self.selected_ledger_var = tk.StringVar()
        self.ledger_combobox = ttk.Combobox(record_frame, textvariable=self.selected_ledger_var, state="readonly", width=20)
        self.ledger_combobox.grid(row=0, column=1, pady=5)
        
        ttk.Label(record_frame, text="资产金额:").grid(row=1, column=0, sticky=tk.W)
        self.amount_var = tk.StringVar()
        ttk.Entry(record_frame, textvariable=self.amount_var, width=20).grid(row=1, column=1, pady=5)
        
        ttk.Label(record_frame, text="备注:").grid(row=2, column=0, sticky=tk.W)
        self.note_var = tk.StringVar()
        ttk.Entry(record_frame, textvariable=self.note_var, width=20).grid(row=2, column=1, pady=5)
        
        ttk.Label(record_frame, text="盘点周期:").grid(row=3, column=0, sticky=tk.W)
        self.period_var = tk.StringVar()
        ttk.Entry(record_frame, textvariable=self.period_var, width=20).grid(row=3, column=1, pady=5)
        ttk.Label(record_frame, text="必填项").grid(row=4, column=1, sticky=tk.W)
        
        ttk.Button(record_frame, text="更新资产", command=self.add_asset_record).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 历史记录区域
        history_frame = ttk.LabelFrame(self.management_frame, text="历史记录", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        history_columns = ("时间", "账本", "金额", "盘点周期", "备注")
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show="headings", height=10)
        self.history_tree.heading("时间", text="时间")
        self.history_tree.heading("账本", text="账本")
        self.history_tree.heading("金额", text="金额")
        self.history_tree.heading("盘点周期", text="盘点周期")
        self.history_tree.heading("备注", text="备注")
        self.history_tree.column("时间", width=120)
        self.history_tree.column("账本", width=80)
        self.history_tree.column("金额", width=80)
        self.history_tree.column("盘点周期", width=80)
        self.history_tree.column("备注", width=150)
        
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def create_asset_statistics_page(self):
        """创建资产统计页面"""
        self.statistics_frame = ttk.Frame(self.content_frame)
        self.statistics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.statistics_frame.columnconfigure(0, weight=1)
        self.statistics_frame.rowconfigure(0, weight=1)
        
        # 统计信息区域 - 使用Canvas和滚动条
        stats_frame = ttk.LabelFrame(self.statistics_frame, text="资产统计", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # 创建Canvas和滚动条用于统计区域
        stats_canvas = tk.Canvas(stats_frame)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=stats_canvas.yview)
        self.stats_scrollable_frame = ttk.Frame(stats_canvas)
        
        # 配置滚动区域
        self.stats_scrollable_frame.bind(
            "<Configure>",
            lambda e: stats_canvas.configure(
                scrollregion=stats_canvas.bbox("all")
            )
        )
        
        stats_canvas.create_window((0, 0), window=self.stats_scrollable_frame, anchor="nw")
        stats_canvas.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 在滚动框架内创建统计内容
        self.create_statistics_content(self.stats_scrollable_frame)
        
        # 绑定鼠标滚轮事件
        stats_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.stats_scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def show_asset_management(self):
        """显示资产管理页面"""
        self.statistics_frame.grid_remove()
        self.management_frame.grid()
        self.asset_mgmt_btn.configure(state="disabled")
        self.asset_stats_btn.configure(state="normal")
    
    def show_asset_statistics(self):
        """显示资产统计页面"""
        self.management_frame.grid_remove()
        self.statistics_frame.grid()
        self.asset_stats_btn.configure(state="disabled")
        self.asset_mgmt_btn.configure(state="normal")
        self.refresh_statistics()
        self.refresh_line_chart()
    
    def refresh_data(self):
        """刷新所有数据"""
        self.refresh_ledger_list()
        self.refresh_ledger_combobox()
        self.refresh_history()
    
    def refresh_ledger_list(self):
        """刷新账本列表"""
        self.ledger_listbox.delete(0, tk.END)
        ledgers = self.db.get_all_ledgers()
        for ledger in ledgers:
            self.ledger_listbox.insert(tk.END, f"{ledger.name} - {ledger.description}")
    
    def refresh_ledger_combobox(self):
        """刷新账本下拉框"""
        ledgers = self.db.get_all_ledgers()
        ledger_names = [ledger.name for ledger in ledgers]
        self.ledger_combobox['values'] = ledger_names
        if ledger_names:
            self.ledger_combobox.set(ledger_names[0])
    
    def refresh_history(self):
        """刷新历史记录"""
        # 清空历史记录表格
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 获取所有记录
        ledgers = {l.id: l.name for l in self.db.get_all_ledgers()}
        records = self.db.get_all_records()
        
        # 按时间排序
        records.sort(key=lambda x: x.created_at, reverse=True)
        
        # 填充数据
        for record in records[:50]:  # 只显示最近50条记录
            ledger_name = ledgers.get(record.ledger_id, "未知")
            self.history_tree.insert("", "end", values=(
                record.created_at.strftime("%Y-%m-%d %H:%M"),
                ledger_name,
                f"¥{record.amount:,.2f}",
                record.period,
                record.note
            ))
    
    def add_ledger(self):
        """添加新账本"""
        name = self.ledger_name_var.get().strip()
        description = self.ledger_desc_var.get().strip()
        
        if not name:
            messagebox.showerror("错误", "请输入账本名称")
            return
        
        try:
            ledger = Ledger(id=None, name=name, description=description, created_at=datetime.now())
            self.db.create_ledger(ledger)
            messagebox.showinfo("成功", "账本创建成功")
            
            # 清空输入框
            self.ledger_name_var.set("")
            self.ledger_desc_var.set("")
            
            # 刷新数据
            self.refresh_data()
            if hasattr(self, 'tree'):  # 如果在统计页面，也刷新统计
                self.refresh_statistics()
        except Exception as e:
            messagebox.showerror("错误", f"创建账本失败: {str(e)}")
    
    def delete_ledger(self):
        """删除选中账本"""
        selection = self.ledger_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的账本")
            return
        
        # 获取选中的账本
        ledgers = self.db.get_all_ledgers()
        if selection[0] >= len(ledgers):
            return
        
        ledger = ledgers[selection[0]]
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除账本 '{ledger.name}' 吗？这将删除该账本的所有记录。"):
            return
        
        try:
            self.db.delete_ledger(ledger.id)
            messagebox.showinfo("成功", "账本删除成功")
            self.refresh_data()
            if hasattr(self, 'tree'):  # 如果在统计页面，也刷新统计
                self.refresh_statistics()
                self.refresh_line_chart()
        except Exception as e:
            messagebox.showerror("错误", f"删除账本失败: {str(e)}")
    
    def on_ledger_select(self, event):
        """账本列表选择事件"""
        selection = self.ledger_listbox.curselection()
        if selection:
            ledgers = self.db.get_all_ledgers()
            if selection[0] < len(ledgers):
                ledger = ledgers[selection[0]]
                self.ledger_name_var.set(ledger.name)
                self.ledger_desc_var.set(ledger.description)
    
    def add_asset_record(self):
        """添加资产记录"""
        ledger_name = self.selected_ledger_var.get()
        amount_str = self.amount_var.get().strip()
        note = self.note_var.get().strip()
        period = self.period_var.get().strip()
        
        if not ledger_name:
            messagebox.showerror("错误", "请选择账本")
            return
        
        if not amount_str:
            messagebox.showerror("错误", "请输入资产金额")
            return
        if not period:
            messagebox.showerror("错误", "请输入资产周期")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的金额")
            return
        
        # 查找账本ID
        ledgers = self.db.get_all_ledgers()
        ledger_id = None
        for ledger in ledgers:
            if ledger.name == ledger_name:
                ledger_id = ledger.id
                break
        
        if ledger_id is None:
            messagebox.showerror("错误", "未找到选中的账本")
            return
        
        try:
            record = AssetRecord(
                id=None,
                ledger_id=ledger_id,
                amount=amount,
                note=note,
                period=period,
                created_at=datetime.now()
            )
            self.db.add_asset_record(record)
            messagebox.showinfo("成功", "资产记录更新成功")
            
            # 清空输入框
            self.amount_var.set("")
            self.note_var.set("")
            self.period_var.set("")
            
            # 刷新数据
            self.refresh_data()
            if hasattr(self, 'tree'):  # 如果在统计页面，也刷新统计
                self.refresh_statistics()
                self.refresh_line_chart()
        except Exception as e:
            messagebox.showerror("错误", f"更新资产记录失败: {str(e)}")
    

    def refresh_statistics(self):
        """刷新统计信息"""
        if not hasattr(self, 'tree'):
            return
            
        summaries = self.db.get_ledger_summaries()
        total_amount = sum(s.current_amount for s in summaries)
        
        # 更新总资产
        self.total_assets_var.set(f"总资产: ¥{total_amount:,.2f}")
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充数据
        for summary in summaries:
            self.tree.insert("", "end", values=(
                summary.ledger.name,
                f"¥{summary.current_amount:,.2f}",
                f"{summary.percentage:.1f}%"
            ))
        
        # 绘制饼图
        self.draw_pie_chart(summaries)

    def refresh_line_chart(self):
        """刷新折线图"""
        if not hasattr(self, 'line_chart_fig'):
            return
            
        # 清除之前的图形
        self.line_chart_fig.clear()
        
        # 获取所有账本
        ledgers = self.db.get_all_ledgers()
        if not ledgers:
            return
        
        # 创建子图
        ax = self.line_chart_fig.add_subplot(111)
        
        # 为每个账本获取历史数据并绘制折线
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", 
                  "#FF9F68", "#A8E6CF", "#FFACAC", "#B5EAD7", "#C7CEEA"]
        
        # 获取所有记录并按日期分组
        all_dates = set()
        ledger_data = {}
        
        for ledger in ledgers:
            records = self.db.get_ledger_history(ledger.id)
            if records:
                # 按日期分组，保留每天最后的记录
                date_amounts = {}
                for record in records:
                    date_key = record.created_at.date()
                    all_dates.add(date_key)
                    # 保留最新的记录
                    if date_key not in date_amounts or record.created_at > datetime.combine(
                        date_key, datetime.min.time().replace()
                    ):
                        date_amounts[date_key] = record.amount
                
                ledger_data[ledger.name] = date_amounts
        
        if not all_dates:
            return
        
        # 排序日期
        sorted_dates = sorted(list(all_dates))
        date_labels = [date.strftime("%m-%d") for date in sorted_dates]
        
        # 绘制每个账本的折线
        for i, (ledger_name, date_amounts) in enumerate(ledger_data.items()):
            amounts = []
            for date in sorted_dates:
                amounts.append(date_amounts.get(date, 0))
            
            color = colors[i % len(colors)]
            ax.plot(date_labels, amounts, marker='o', linewidth=2, label=ledger_name, color=color)
        
        # 绘制总资产折线
        total_amounts = []
        for date in sorted_dates:
            total = sum([data.get(date, 0) for data in ledger_data.values()])
            total_amounts.append(total)
        
        ax.plot(date_labels, total_amounts, marker='s', linewidth=3, label='总资产', color='black')
        
        # 设置图形属性
        ax.set_xlabel("日期")
        ax.set_ylabel("金额 (¥)")
        ax.set_title("资产变化趋势")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签以避免重叠
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        
        # 自动调整布局
        self.line_chart_fig.tight_layout()
        
        # 刷新画布
        self.line_chart_canvas.draw()

    def draw_pie_chart(self, summaries):
        """绘制资产配置饼图"""
        if not hasattr(self, 'chart_canvas'):
            return
            
        self.chart_canvas.delete("all")
        
        if not summaries:
            return
        
        # 计算总金额
        total = sum(s.current_amount for s in summaries)
        if total <= 0:
            return
        
        # 获取画布尺寸
        canvas_width = self.chart_canvas.winfo_width()
        canvas_height = self.chart_canvas.winfo_height()
        
        # 如果尺寸为1，说明还未正确初始化，使用默认值
        if canvas_width <= 1:
            canvas_width = 500
        if canvas_height <= 1:
            canvas_height = 300
        
        # 设置饼图参数
        center_x, center_y = canvas_width // 2, canvas_height // 2
        radius = min(canvas_width, canvas_height) // 3
        
        # 颜色列表
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", 
                  "#FF9F68", "#A8E6CF", "#FFACAC", "#B5EAD7", "#C7CEEA"]
        
        # 绘制饼图
        start_angle = 0
        for i, summary in enumerate(summaries):
            # 计算角度
            extent = 360 * (summary.current_amount / total)
            
            # 选择颜色
            color = colors[i % len(colors)]
            
            # 绘制扇形
            if extent > 0:  # 只绘制有值的部分
                self.chart_canvas.create_arc(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    start=start_angle, extent=extent,
                    fill=color, outline="white", width=2
                )
            
            # 绘制标签
            percentage = summary.current_amount / total * 100
            if percentage > 5:  # 只显示占比大于5%的标签
                # 计算标签位置
                mid_angle = start_angle + extent / 2
                radians = mid_angle * math.pi / 180  # 使用math.pi
                
                # 标签位置稍微远离饼图中心
                label_radius = radius + 30
                label_x = center_x + label_radius * math.cos(radians)  # 使用math.cos
                label_y = center_y - label_radius * math.sin(radians)  # 使用math.sin
                
                self.chart_canvas.create_text(
                    label_x, label_y,
                    text=f"{summary.ledger.name}\n{percentage:.1f}%",
                    font=("Arial", 9),
                    anchor="center"
                )
            
            start_angle += extent

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        canvas = event.widget
        if isinstance(canvas, tk.Canvas):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # 如果事件来自框架，找到其父Canvas
            parent = canvas.master
            while parent and not isinstance(parent, tk.Canvas):
                parent = parent.master
            if parent and isinstance(parent, tk.Canvas):
                parent.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_resize(self, event):
        """画布大小改变时重绘饼图"""
        if hasattr(self, '_after_id'):
            self.chart_canvas.after_cancel(self._after_id)
        self._after_id = self.chart_canvas.after(100, self.refresh_statistics)

    def create_statistics_content(self, parent):
        """创建统计内容区域"""
        # 总资产显示
        self.total_assets_var = tk.StringVar(value="总资产: ¥0.00")
        total_label = ttk.Label(parent, textvariable=self.total_assets_var, font=("Arial", 12, "bold"))
        total_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 资产配置饼图
        chart_frame = ttk.Frame(parent)
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        chart_frame.columnconfigure(0, weight=1)
        
        self.chart_canvas = tk.Canvas(chart_frame, height=300, bg="white")
        self.chart_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 调整画布大小以适应内容
        self.chart_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # 折线图区域
        line_chart_frame = ttk.Frame(parent)
        line_chart_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        line_chart_frame.columnconfigure(0, weight=1)
        line_chart_frame.rowconfigure(0, weight=1)
        
        # 创建matplotlib图形
        self.line_chart_fig = plt.Figure(figsize=(10, 4), dpi=100)
        self.line_chart_canvas = FigureCanvasTkAgg(self.line_chart_fig, line_chart_frame)
        self.line_chart_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 账本详情表格
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        
        columns = ("账本", "金额", "占比")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("账本", text="账本")
        self.tree.heading("金额", text="金额")
        self.tree.heading("占比", text="占比")
        self.tree.column("账本", width=150)
        self.tree.column("金额", width=100)
        self.tree.column("占比", width=100)
        
        # 添加滚动条到表格
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置表格框架的行权重
        table_frame.rowconfigure(0, weight=1)