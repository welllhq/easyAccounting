# ui.py 
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QFrame, QApplication,
                               QGroupBox, QLineEdit, QTextEdit, QComboBox, QTableWidget,
                               QTableWidgetItem, QLabel, QMessageBox, QListWidget, 
                               QGridLayout, QScrollArea, QDateEdit)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
from database import Database
from models import Ledger, AssetRecord
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("资产盘点")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建菜单按钮区域
        self.create_menu_bar(main_layout)
        
        # 创建页面容器
        self.create_page_container(main_layout)
        
        # 默认显示资产管理页面
        self.show_asset_management()
    
    def create_menu_bar(self, parent_layout):
        """创建顶部菜单按钮"""
        menu_frame = QFrame()
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(10)
        
        # 资产管理按钮
        self.asset_management_btn = QPushButton("资产盘点")
        self.asset_management_btn.setFixedHeight(40)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.asset_management_btn.setFont(font)
        self.asset_management_btn.clicked.connect(self.show_asset_management)
        
        # 资产统计按钮
        self.asset_statistics_btn = QPushButton("资产统计")
        self.asset_statistics_btn.setFixedHeight(40)
        self.asset_statistics_btn.setFont(font)
        self.asset_statistics_btn.clicked.connect(self.show_asset_statistics)
        
        # 添加按钮到布局
        menu_layout.addWidget(self.asset_management_btn)
        menu_layout.addWidget(self.asset_statistics_btn)
        menu_layout.addStretch()  # 添加弹性空间
        
        parent_layout.addWidget(menu_frame)
    
    def create_page_container(self, parent_layout):
        """创建页面容器"""
        self.stacked_widget = QStackedWidget()
        parent_layout.addWidget(self.stacked_widget)
        
        # 创建页面实例
        self.asset_management_page = AssetManagementPage(self.db)
        self.asset_statistics_page = AssetStatisticsPage(self.db)
        
        # 添加页面到堆栈
        self.stacked_widget.addWidget(self.asset_management_page)
        self.stacked_widget.addWidget(self.asset_statistics_page)
    
    def show_asset_management(self):
        """显示资产盘点页面"""
        self.stacked_widget.setCurrentIndex(0)
        self.asset_management_btn.setEnabled(False)
        self.asset_statistics_btn.setEnabled(True)
    
    def show_asset_statistics(self):
        """显示资产统计页面"""
        self.stacked_widget.setCurrentIndex(1)
        self.asset_statistics_btn.setEnabled(False)
        self.asset_management_btn.setEnabled(True)
        self.asset_statistics_page.refresh_statistics()

# 资产管理页面类
class AssetManagementPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("资产盘点")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 创建主内容区域（水平布局）
        main_content_layout = QHBoxLayout()
        main_content_layout.setSpacing(10)
        
        # 左侧：账本管理区域
        self.create_ledger_management_group(main_content_layout)
        
        # 右侧：资产记录区域
        self.create_asset_record_group(main_content_layout)
        
        layout.addLayout(main_content_layout)
        
        # 下方：历史记录区域
        self.create_history_group(layout)
    
    def create_ledger_management_group(self, parent_layout):
        """创建账本管理区域"""
        ledger_group = QGroupBox("账本管理")
        ledger_layout = QVBoxLayout(ledger_group)
        ledger_layout.setSpacing(10)
        
        # 账本名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("账本名称:"))
        self.ledger_name_input = QLineEdit()
        name_layout.addWidget(self.ledger_name_input)
        ledger_layout.addLayout(name_layout)
        
        # 账本描述输入
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.ledger_desc_input = QLineEdit()
        desc_layout.addWidget(self.ledger_desc_input)
        ledger_layout.addLayout(desc_layout)
        
        # 添加账本按钮
        add_ledger_btn = QPushButton("添加账本")
        add_ledger_btn.clicked.connect(self.add_ledger)
        ledger_layout.addWidget(add_ledger_btn)
        
        # 账本列表标题
        ledger_list_label = QLabel("现有账本:")
        ledger_list_label.setStyleSheet("font-weight: bold;")
        ledger_layout.addWidget(ledger_list_label)
        
        # 账本列表
        self.ledger_list_widget = QListWidget()
        self.ledger_list_widget.itemSelectionChanged.connect(self.on_ledger_selected)
        ledger_layout.addWidget(self.ledger_list_widget)
        
        # 删除账本按钮
        delete_ledger_btn = QPushButton("删除选中账本")
        delete_ledger_btn.clicked.connect(self.delete_ledger)
        ledger_layout.addWidget(delete_ledger_btn)
        
        parent_layout.addWidget(ledger_group)
    
    def create_asset_record_group(self, parent_layout):
        """创建资产记录区域"""
        record_group = QGroupBox("资产记录")
        record_layout = QVBoxLayout(record_group)
        record_layout.setSpacing(10)
        
        # 选择账本
        ledger_select_layout = QHBoxLayout()
        ledger_select_layout.addWidget(QLabel("选择账本:"))
        self.ledger_combobox = QComboBox()
        ledger_select_layout.addWidget(self.ledger_combobox)
        record_layout.addLayout(ledger_select_layout)
        
       
        # 盘点日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("盘点日期:"))
        self.date_input = QDateEdit()
        self.date_input.setDateTime(QDateTime.currentDateTime())  # 默认为当前日期时间
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.date_input.setCalendarPopup(True)  # 启用日历弹窗
        date_layout.addWidget(self.date_input)
        record_layout.addLayout(date_layout)

        # 资产金额
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("资产金额:"))
        self.amount_input = QLineEdit()
        amount_layout.addWidget(self.amount_input)
        record_layout.addLayout(amount_layout)
        
        # 备注
        note_layout = QHBoxLayout()
        note_layout.addWidget(QLabel("备注:"))
        self.note_input = QLineEdit()
        note_layout.addWidget(self.note_input)
        record_layout.addLayout(note_layout)
        
        # 盘点周期
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("盘点周期:"))
        self.period_input = QLineEdit()
        period_layout.addWidget(self.period_input)
        record_layout.addLayout(period_layout)
        
        # 周期说明
        period_note = QLabel("例子：xx年年初第n次盘点")
        period_note.setStyleSheet("color: red; font-size: 10px;")
        record_layout.addWidget(period_note)
        
        # 更新资产按钮
        update_asset_btn = QPushButton("更新资产")
        update_asset_btn.clicked.connect(self.add_asset_record)
        record_layout.addWidget(update_asset_btn)
        
        parent_layout.addWidget(record_group)
    
    def create_history_group(self, parent_layout):
        """创建历史记录区域"""
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout(history_group)
        
        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["时间", "账本", "金额", "盘点周期", "备注"])
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为只读
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        
        parent_layout.addWidget(history_group)
    
    def refresh_data(self):
        """刷新所有数据"""
        self.refresh_ledger_list()
        self.refresh_ledger_combobox()
        self.refresh_history()
    
    def refresh_ledger_list(self):
        """刷新账本列表"""
        self.ledger_list_widget.clear()
        ledgers = self.db.get_all_ledgers()
        self.ledger_objects = ledgers  # 保存账本对象引用
        
        for ledger in ledgers:
            item_text = f"{ledger.name} - {ledger.description}"
            self.ledger_list_widget.addItem(item_text)
    
    def refresh_ledger_combobox(self):
        """刷新账本下拉框"""
        self.ledger_combobox.clear()
        ledgers = self.db.get_all_ledgers()
        self.ledger_combo_objects = ledgers  # 保存账本对象引用
        
        for ledger in ledgers:
            self.ledger_combobox.addItem(ledger.name)
    
    def refresh_history(self):
        """刷新历史记录"""
        # 清空表格
        self.history_table.setRowCount(0)
        
        # 获取所有记录
        ledgers = {l.id: l.name for l in self.db.get_all_ledgers()}
        records = self.db.get_all_records()
        
        # 按时间排序
        records.sort(key=lambda x: x.created_at, reverse=True)
        
        # 填充数据
        self.history_table.setRowCount(min(len(records), 50))  # 只显示最近50条记录
        
        for row, record in enumerate(records[:50]):
            ledger_name = ledgers.get(record.ledger_id, "未知")
            
            self.history_table.setItem(row, 0, QTableWidgetItem(record.created_at.strftime("%Y-%m-%d %H:%M")))
            self.history_table.setItem(row, 1, QTableWidgetItem(ledger_name))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"¥{record.amount:,.2f}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(record.period))
            self.history_table.setItem(row, 4, QTableWidgetItem(record.note))
    
    def add_ledger(self):
        """添加新账本"""
        name = self.ledger_name_input.text().strip()
        description = self.ledger_desc_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "错误", "请输入账本名称")
            return
        
        try:
            from datetime import datetime
            ledger = Ledger(id=None, name=name, description=description, created_at=datetime.now())
            self.db.create_ledger(ledger)
            QMessageBox.information(self, "成功", "账本创建成功")
            
            # 清空输入框
            self.ledger_name_input.clear()
            self.ledger_desc_input.clear()
            
            # 刷新数据
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建账本失败: {str(e)}")
    
    def delete_ledger(self):
        """删除选中账本"""
        selected_items = self.ledger_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的账本")
            return
        
        # 获取选中的账本
        selected_row = self.ledger_list_widget.currentRow()
        if selected_row >= len(self.ledger_objects):
            return
        
        ledger = self.ledger_objects[selected_row]
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除账本 '{ledger.name}' 吗？这将删除该账本的所有记录。")
        if reply == QMessageBox.No:
            return
        
        try:
            self.db.delete_ledger(ledger.id)
            QMessageBox.information(self, "成功", "账本删除成功")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除账本失败: {str(e)}")
    
    def on_ledger_selected(self):
        """账本列表选择事件"""
        selected_items = self.ledger_list_widget.selectedItems()
        if selected_items:
            selected_row = self.ledger_list_widget.currentRow()
            if selected_row < len(self.ledger_objects):
                ledger = self.ledger_objects[selected_row]
                self.ledger_name_input.setText(ledger.name)
                self.ledger_desc_input.setText(ledger.description)
    
    def add_asset_record(self):
        """添加资产记录"""
        ledger_name = self.ledger_combobox.currentText()
        amount_str = self.amount_input.text().strip()
        note = self.note_input.text().strip()
        period = self.period_input.text().strip()
        created_at = self.date_input.dateTime().toPython()
        
        if not ledger_name:
            QMessageBox.warning(self, "错误", "请选择账本")
            return
        
        if not amount_str:
            QMessageBox.warning(self, "错误", "请输入资产金额")
            return
        
        
        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的金额")
            return
        
        # 查找账本ID
        ledger_id = None
        for ledger in self.ledger_combo_objects:
            if ledger.name == ledger_name:
                ledger_id = ledger.id
                break
        
        if ledger_id is None:
            QMessageBox.warning(self, "错误", "未找到选中的账本")
            return
        
        try:
            from datetime import datetime
            record = AssetRecord(
                id=None,
                ledger_id=ledger_id,
                amount=amount,
                note=note,
                period=period,
                created_at=created_at
            )
            self.db.add_asset_record(record)
            QMessageBox.information(self, "成功", "资产记录更新成功")
            
            # 清空输入框
            self.amount_input.clear()
            self.note_input.clear()
            self.period_input.clear()
            
            # 刷新数据
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新资产记录失败: {str(e)}")



class AssetStatisticsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.refresh_statistics()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("资产统计")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 总资产显示
        self.total_assets_label = QLabel("总资产: ¥0.00")
        total_assets_font = QFont()
        total_assets_font.setPointSize(12)
        total_assets_font.setBold(True)
        self.total_assets_label.setFont(total_assets_font)
        layout.addWidget(self.total_assets_label)
        
        # 创建滚动区域用于统计内容
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # 创建包含图表的框架（左右布局）
        charts_frame = QFrame()
        charts_layout = QHBoxLayout(charts_frame)
        charts_layout.setSpacing(10)
        
        # 饼图区域
        self.create_pie_chart_area(charts_layout)
        
        # 折线图区域
        self.create_line_chart_area(charts_layout)
        
        scroll_layout.addWidget(charts_frame)
        
        # 账本详情表格
        self.create_ledger_table_area(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def create_pie_chart_area(self, parent_layout):
        """创建饼图区域"""
        chart_group = QGroupBox("资产配置饼图")
        chart_layout = QVBoxLayout(chart_group)
    
        # 创建matplotlib图形和画布
        self.pie_fig = Figure(figsize=(6, 5), dpi=100)
        self.pie_canvas = FigureCanvas(self.pie_fig)
        chart_layout.addWidget(self.pie_canvas)
    
        parent_layout.addWidget(chart_group)
    
    def create_line_chart_area(self, parent_layout):
        """创建折线图区域"""
        chart_group = QGroupBox("资产变化趋势")
        chart_layout = QVBoxLayout(chart_group)
    
        # 创建matplotlib图形和画布
        self.line_fig = Figure(figsize=(8, 5), dpi=100)
        self.line_canvas = FigureCanvas(self.line_fig)
        chart_layout.addWidget(self.line_canvas)
    
        parent_layout.addWidget(chart_group)
    
    def create_ledger_table_area(self, parent_layout):
        """创建账本详情表格区域"""
        table_group = QGroupBox("账本详情")
        table_layout = QVBoxLayout(table_group)
        
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(3)
        self.ledger_table.setHorizontalHeaderLabels(["账本", "金额", "占比"])
        self.ledger_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ledger_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.ledger_table)
        
        parent_layout.addWidget(table_group)
    
    def refresh_statistics(self):
        """刷新统计信息"""
        # 获取账本统计信息
        summaries = self.db.get_ledger_summaries()
        total_amount = sum(s.current_amount for s in summaries)
        
        # 更新总资产
        self.total_assets_label.setText(f"总资产: ¥{total_amount:,.2f}")
        
        # 更新表格
        self.ledger_table.setRowCount(len(summaries))
        for row, summary in enumerate(summaries):
            self.ledger_table.setItem(row, 0, QTableWidgetItem(summary.ledger.name))
            self.ledger_table.setItem(row, 1, QTableWidgetItem(f"¥{summary.current_amount:,.2f}"))
            self.ledger_table.setItem(row, 2, QTableWidgetItem(f"{summary.percentage:.1f}%"))
        
        # 绘制饼图
        self.draw_pie_chart(summaries)
        
        # 绘制折线图
        self.draw_line_chart()
    
    def draw_pie_chart(self, summaries):
        """绘制资产配置饼图"""
        # 清除之前的图形
        self.pie_fig.clear()
    
        if not summaries:
            ax = self.pie_fig.add_subplot(111)
            ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', transform=ax.transAxes)
            self.pie_canvas.draw()
            return
    
        # 计算总金额
        total = sum(s.current_amount for s in summaries)
        if total <= 0:
            ax = self.pie_fig.add_subplot(111)
            ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', transform=ax.transAxes)
            self.pie_canvas.draw()
            return
    
        # 创建子图
        ax = self.pie_fig.add_subplot(111)
    
        # 准备数据
        sizes = [s.current_amount for s in summaries]
        labels = [s.ledger.name for s in summaries]
    
        # 颜色列表
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", 
                  "#FF9F68", "#A8E6CF", "#FFACAC", "#B5EAD7", "#C7CEEA"]
    
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                          colors=colors[:len(sizes)], startangle=90)
    
        # 设置标题
        ax.set_title("资产配置分布")
    
        # 调整标签字体大小
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)
    
        # 自动调整布局并刷新画布
        self.pie_fig.tight_layout()
        self.pie_canvas.draw()
    
    def draw_line_chart(self):
        """绘制资产变化趋势折线图"""
        # 清除之前的图形
        self.line_fig.clear()
    
        # 获取所有账本
        ledgers = self.db.get_all_ledgers()
        if not ledgers:
            ax = self.line_fig.add_subplot(111)
            ax.text(0.5, 0.5, "暂无数据", ha='center', va='center', transform=ax.transAxes)
            self.line_canvas.draw()
            return
    
        # 创建子图
        ax = self.line_fig.add_subplot(111)
    
        # 颜色列表
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", 
                  "#FF9F68", "#A8E6CF", "#FFACAC", "#B5EAD7", "#C7CEEA"]
    
        # 为每个账本获取历史数据并绘制折线
        for i, ledger in enumerate(ledgers):
            records = self.db.get_ledger_history(ledger.id)
            if not records:
                continue
        
            # 按时间排序
            records.sort(key=lambda x: x.created_at)

            # 只取最近的8条记录
            records = records[:8]
        
            # 准备数据
            x_data = []
            y_data = []
        
            for record in records:
                # 使用 period 字段作为横坐标，如果为空则使用 created_at
                if record.period and record.period.strip():
                    x_data.append(record.period)
                else:
                    x_data.append(record.created_at.strftime("%Y-%m-%d"))
                y_data.append(record.amount)
        
            # 绘制折线
            color = colors[i % len(colors)]
            ax.plot(x_data, y_data, marker='o', linewidth=2, label=ledger.name, color=color)
    
        # 设置图形属性
        ax.set_xlabel("周期/日期")
        ax.set_ylabel("金额 (¥)")
        ax.set_title("资产变化趋势")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
        # 旋转x轴标签以避免重叠
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
    
        # 自动调整布局并刷新画布
        self.line_fig.tight_layout()
        self.line_canvas.draw()